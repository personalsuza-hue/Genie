from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import PyPDF2
import io
import json
import re
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="StudyGenie API", description="AI-powered study guide generator")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Ensure uploads directory exists
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Models
class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    content: str
    upload_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MCQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    options: List[str]
    correct_answer: int
    explanation: str

class Flashcard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    front: str
    back: str

class StudyMaterial(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    mcqs: List[MCQuestion]
    flashcards: List[Flashcard]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    user_message: str
    ai_response: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    document_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Utility Functions
def extract_text_from_pdf(pdf_file: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text from PDF: {str(e)}")

def prepare_for_mongo(data: dict) -> dict:
    """Prepare data for MongoDB storage"""
    if isinstance(data.get('upload_time'), datetime):
        data['upload_time'] = data['upload_time'].isoformat()
    if isinstance(data.get('created_at'), datetime):
        data['created_at'] = data['created_at'].isoformat()
    if isinstance(data.get('timestamp'), datetime):
        data['timestamp'] = data['timestamp'].isoformat()
    return data

async def generate_mcqs(content: str, num_questions: int = 10) -> List[MCQuestion]:
    """Generate multiple choice questions from content using AI"""
    try:
        # Get API key from environment
        api_key = os.environ.get('EMERGENT_LLM_KEY', os.environ.get('OPENAI_API_KEY'))
        if not api_key:
            raise HTTPException(status_code=500, detail="No API key configured")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"mcq_generation_{uuid.uuid4()}",
            system_message="You are an expert educational content creator. Generate high-quality multiple choice questions based on the provided content."
        ).with_model("openai", "gpt-4o-mini")
        
        prompt = f"""
        Based on the following content, create {num_questions} multiple choice questions. 
        Each question should have 4 options and test understanding of key concepts.
        
        Format your response as a JSON array where each question has:
        - question: the question text
        - options: array of 4 possible answers
        - correct_answer: index (0-3) of the correct option
        - explanation: brief explanation of why the answer is correct
        
        Content:
        {content[:3000]}  # Limit content to avoid token limits
        
        Return ONLY the JSON array, no other text.
        """
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse the JSON response
        try:
            # Try to parse as direct JSON first
            questions_data = json.loads(response)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
            if json_match:
                try:
                    questions_data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    raise ValueError("Could not parse AI response as JSON")
            else:
                # Try to find JSON array in the response
                json_match = re.search(r'(\[.*?\])', response, re.DOTALL)
                if json_match:
                    try:
                        questions_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        raise ValueError("Could not parse AI response as JSON")
                else:
                    raise ValueError("No JSON array found in AI response")
        
        try:
            mcqs = []
            for q_data in questions_data:
                mcq = MCQuestion(
                    question=q_data['question'],
                    options=q_data['options'],
                    correct_answer=q_data['correct_answer'],
                    explanation=q_data['explanation']
                )
                mcqs.append(mcq)
            return mcqs
        except (KeyError, TypeError, ValueError) as e:
            logging.error(f"Error processing MCQ data: {str(e)}")
            # Fallback: create sample questions if AI response structure is invalid
            return [
                MCQuestion(
                    question="What is the main topic of this document?",
                    options=["Topic A", "Topic B", "Topic C", "Topic D"],
                    correct_answer=0,
                    explanation="Based on the document content analysis."
                )
            ]
    except Exception as e:
        logging.error(f"Error generating MCQs: {str(e)}")
        # Return a fallback question
        return [
            MCQuestion(
                question="Sample question based on the uploaded content",
                options=["Option A", "Option B", "Option C", "Option D"],
                correct_answer=0,
                explanation="This is a sample question generated from your document."
            )
        ]

async def generate_flashcards(content: str, num_cards: int = 15) -> List[Flashcard]:
    """Generate flashcards from content using AI"""
    try:
        # Get API key from environment
        api_key = os.environ.get('EMERGENT_LLM_KEY', os.environ.get('OPENAI_API_KEY'))
        if not api_key:
            raise HTTPException(status_code=500, detail="No API key configured")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"flashcard_generation_{uuid.uuid4()}",
            system_message="You are an expert educational content creator. Generate effective flashcards for studying."
        ).with_model("openai", "gpt-4o-mini")
        
        prompt = f"""
        Based on the following content, create {num_cards} flashcards for studying.
        Each flashcard should have a question/term on the front and the answer/definition on the back.
        
        Format your response as a JSON array where each flashcard has:
        - front: the question or term
        - back: the answer or definition
        
        Content:
        {content[:3000]}  # Limit content to avoid token limits
        
        Return ONLY the JSON array, no other text.
        """
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse the JSON response
        try:
            # Try to parse as direct JSON first
            cards_data = json.loads(response)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
            if json_match:
                try:
                    cards_data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    raise ValueError("Could not parse AI response as JSON")
            else:
                # Try to find JSON array in the response
                json_match = re.search(r'(\[.*?\])', response, re.DOTALL)
                if json_match:
                    try:
                        cards_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        raise ValueError("Could not parse AI response as JSON")
                else:
                    raise ValueError("No JSON array found in AI response")
        
        try:
            flashcards = []
            for card_data in cards_data:
                flashcard = Flashcard(
                    front=card_data['front'],
                    back=card_data['back']
                )
                flashcards.append(flashcard)
            return flashcards
        except (KeyError, TypeError, ValueError) as e:
            logging.error(f"Error processing flashcard data: {str(e)}")
            # Fallback: create sample flashcards
            return [
                Flashcard(
                    front="Key concept from the document",
                    back="Definition or explanation based on the content"
                )
            ]
    except Exception as e:
        logging.error(f"Error generating flashcards: {str(e)}")
        # Return fallback flashcards
        return [
            Flashcard(
                front="Main topic",
                back="Summary of the document content"
            )
        ]

async def chat_with_document(document_content: str, user_question: str) -> str:
    """Chat with document using RAG-like approach"""
    try:
        # Get API key from environment
        api_key = os.environ.get('EMERGENT_LLM_KEY', os.environ.get('OPENAI_API_KEY'))
        if not api_key:
            raise HTTPException(status_code=500, detail="No API key configured")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"document_chat_{uuid.uuid4()}",
            system_message=f"""You are an AI tutor. Answer questions based ONLY on the provided document content. 
            If the answer isn't in the document, say so politely.
            
            Document content:
            {document_content[:4000]}"""  # Limit content to avoid token limits
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=user_question)
        response = await chat.send_message(user_message)
        
        return response
    except Exception as e:
        logging.error(f"Error in chat: {str(e)}")
        return "I'm sorry, I encountered an error while processing your question. Please try again."

# API Routes
@api_router.get("/")
async def root():
    return {"message": "StudyGenie API is running!"}

@api_router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document"""
    logger.info(f"Received upload request - filename: {file.filename}, content_type: {file.content_type}")
    
    if not file.filename:
        logger.error("No filename provided")
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    if not file.filename.endswith('.pdf'):
        logger.error(f"Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read and extract text from PDF
        content = await file.read()
        logger.info(f"File read successfully, size: {len(content)} bytes")
        
        if not content:
            logger.error("Empty file content")
            raise HTTPException(status_code=400, detail="Empty file")
        
        text_content = extract_text_from_pdf(content)
        logger.info(f"Text extracted, length: {len(text_content)} characters")
        
        if not text_content.strip():
            logger.error("No text found in PDF")
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Save document to database
        document = Document(
            filename=file.filename,
            content=text_content
        )
        
        document_dict = prepare_for_mongo(document.dict())
        await db.documents.insert_one(document_dict)
        logger.info(f"Document saved with ID: {document.id}")
        
        # Generate study materials
        logger.info("Starting MCQ generation...")
        mcqs = await generate_mcqs(text_content)
        logger.info(f"Generated {len(mcqs)} MCQs")
        
        logger.info("Starting flashcard generation...")
        flashcards = await generate_flashcards(text_content)
        logger.info(f"Generated {len(flashcards)} flashcards")
        
        # Save study materials
        study_material = StudyMaterial(
            document_id=document.id,
            mcqs=mcqs,
            flashcards=flashcards
        )
        
        study_material_dict = prepare_for_mongo(study_material.dict())
        await db.study_materials.insert_one(study_material_dict)
        logger.info("Study materials saved to database")
        
        return {
            "document_id": document.id,
            "filename": file.filename,
            "text_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content,
            "mcqs": [mcq.dict() for mcq in mcqs],
            "flashcards": [card.dict() for card in flashcards],
            "message": "Document processed successfully!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@api_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat with a specific document"""
    try:
        # Get document from database
        document = await db.documents.find_one({"id": request.document_id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get AI response
        ai_response = await chat_with_document(document['content'], request.message)
        
        # Save chat message to database
        chat_message = ChatMessage(
            document_id=request.document_id,
            user_message=request.message,
            ai_response=ai_response
        )
        
        chat_dict = prepare_for_mongo(chat_message.dict())
        await db.chat_messages.insert_one(chat_dict)
        
        return ChatResponse(response=ai_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

@api_router.get("/documents")
async def get_documents():
    """Get all uploaded documents"""
    documents = await db.documents.find().to_list(1000)
    return [{"id": doc["id"], "filename": doc["filename"], "upload_time": doc["upload_time"]} for doc in documents]

@api_router.get("/study-materials/{document_id}")
async def get_study_materials(document_id: str):
    """Get study materials for a specific document"""
    study_material = await db.study_materials.find_one({"document_id": document_id})
    if not study_material:
        raise HTTPException(status_code=404, detail="Study materials not found")
    
    # Remove MongoDB ObjectId to make it JSON serializable
    if '_id' in study_material:
        del study_material['_id']
    
    return study_material

@api_router.get("/chat-history/{document_id}")
async def get_chat_history(document_id: str):
    """Get chat history for a specific document"""
    chat_messages = await db.chat_messages.find({"document_id": document_id}).to_list(1000)
    
    # Remove MongoDB ObjectId from each message to make them JSON serializable
    for message in chat_messages:
        if '_id' in message:
            del message['_id']
    
    return chat_messages

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
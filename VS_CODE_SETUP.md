# StudyGenie - VS Code Local Development Setup

This guide will help you run the StudyGenie application locally using VS Code.

## Prerequisites

1. **Python 3.8+** - Check with `python --version`
2. **Node.js 16+** - Check with `node --version`
3. **Yarn** - Check with `yarn --version`
4. **MongoDB** - Install MongoDB Community Edition and ensure it's running on `localhost:27017`

## Project Structure

```
/app/
├── backend/         # FastAPI backend (Python)
├── frontend/        # React frontend (JavaScript)
├── requirements.txt # Python dependencies (in backend folder)
└── VS_CODE_SETUP.md # This file
```

## Setup Instructions

### 1. Open in VS Code
- Open VS Code
- File → Open Folder → Select the `/app` directory

### 2. Setup Backend (Python/FastAPI)

Open a terminal in VS Code (Terminal → New Terminal) and run:

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python server.py
```

The backend will start on `http://localhost:8001`

**Alternative using uvicorn:**
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Setup Frontend (React)

Open a **second terminal** in VS Code (click the + button in terminal panel) and run:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
yarn install

# Start the development server
yarn start
```

The frontend will start on `http://localhost:3000` and automatically open in your browser.

## Accessing the Application

1. **Frontend**: http://localhost:3000
2. **Backend API**: http://localhost:8001
3. **API Documentation**: http://localhost:8001/docs (FastAPI auto-generated docs)

## Key Features

- **PDF Upload**: Upload PDF documents for study material generation
- **AI-Generated MCQs**: Get multiple choice questions based on your content
- **Flashcards**: Interactive flashcards for studying
- **AI Chat**: Chat with your documents using AI

## Development Workflow

1. **Backend Development**: 
   - Edit files in `/backend/`
   - Server auto-reloads on changes (thanks to `--reload` flag)

2. **Frontend Development**:
   - Edit files in `/frontend/src/`
   - Hot-reload is enabled, changes appear instantly

## Environment Variables

### Backend (`.env` file in `/backend/`)
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY=sk-emergent-729C7A1E08901341e4
```

### Frontend (`.env` file in `/frontend/`)
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is installed and running
- Check if MongoDB service is active: `brew services start mongodb/brew/mongodb-community` (Mac) or `sudo systemctl start mongod` (Linux)

### Port Already in Use
- Backend (8001): Kill process using `lsof -ti:8001 | xargs kill -9`
- Frontend (3000): Kill process using `lsof -ti:3000 | xargs kill -9`

### Dependencies Issues
- Backend: Try `pip install --upgrade pip` then `pip install -r requirements.txt`
- Frontend: Try `yarn install --force` or delete `node_modules` and run `yarn install`

## VS Code Extensions (Recommended)

1. **Python** - Python language support
2. **Pylance** - Enhanced Python language server
3. **ES7+ React/Redux/React-Native snippets** - React code snippets
4. **Prettier** - Code formatter
5. **Thunder Client** - API testing (alternative to Postman)

## API Testing

You can test the API endpoints using:
1. **FastAPI Docs**: http://localhost:8001/docs
2. **Thunder Client** (VS Code extension)
3. **Postman** or **Insomnia**

### Sample API Endpoints:
- `GET /api/` - Health check
- `POST /api/upload` - Upload PDF
- `GET /api/documents` - List documents
- `GET /api/study-materials/{document_id}` - Get study materials
- `POST /api/chat` - Chat with document

## Development Tips

1. **Use VS Code's integrated terminals** to run both services side by side
2. **Enable format on save** for consistent code formatting
3. **Use the debugger** for Python backend debugging
4. **Install React Developer Tools** browser extension for frontend debugging
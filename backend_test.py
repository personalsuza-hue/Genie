import requests
import sys
import json
import io
from datetime import datetime
import time

class StudyGenieAPITester:
    def __init__(self, base_url="https://ai-tutor-9.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.document_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {}
        if data and not files:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response preview: {str(response_data)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def create_sample_pdf(self):
        """Create a proper PDF for testing"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            import io
            
            # Create PDF in memory
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            
            # Add content to PDF
            p.drawString(100, 750, "Sample Study Document")
            p.drawString(100, 720, "Chapter 1: Introduction to Machine Learning")
            p.drawString(100, 690, "Machine learning is a subset of artificial intelligence that focuses on algorithms")
            p.drawString(100, 660, "that can learn from data. There are three main types of machine learning:")
            p.drawString(100, 630, "1. Supervised Learning: Uses labeled data to train models")
            p.drawString(100, 600, "2. Unsupervised Learning: Finds patterns in unlabeled data")
            p.drawString(100, 570, "3. Reinforcement Learning: Learns through interaction with environment")
            p.drawString(100, 540, "Key Concepts:")
            p.drawString(100, 510, "- Training Data: The dataset used to train the model")
            p.drawString(100, 480, "- Features: Input variables used to make predictions")
            p.drawString(100, 450, "- Labels: The target variable we want to predict")
            p.drawString(100, 420, "- Overfitting: When a model performs well on training data but poorly on new data")
            
            p.showPage()
            p.save()
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except ImportError:
            # Fallback: create a minimal PDF manually
            # This is a very basic PDF structure
            pdf_content = """%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Sample Study Document) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
            return pdf_content.encode('utf-8')

    def test_upload_document(self):
        """Test document upload endpoint"""
        # Create sample PDF content using a minimal valid PDF structure
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj

4 0 obj
<<
/Length 200
>>
stream
BT
/F1 12 Tf
100 700 Td
(Sample Study Document) Tj
0 -20 Td
(Chapter 1: Introduction to Machine Learning) Tj
0 -20 Td
(Machine learning is a subset of artificial intelligence) Tj
0 -20 Td
(that focuses on algorithms that can learn from data.) Tj
0 -20 Td
(There are three main types of machine learning:) Tj
0 -20 Td
(1. Supervised Learning) Tj
0 -20 Td
(2. Unsupervised Learning) Tj
0 -20 Td
(3. Reinforcement Learning) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000356 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
605
%%EOF"""
        
        files = {
            'file': ('sample_study_guide.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        
        success, response = self.run_test(
            "Upload PDF Document", 
            "POST", 
            "upload", 
            200,  # Expecting 200 for successful upload
            files=files
        )
        
        if success and 'document_id' in response:
            self.document_id = response['document_id']
            print(f"   Document ID: {self.document_id}")
            print(f"   MCQs generated: {len(response.get('mcqs', []))}")
            print(f"   Flashcards generated: {len(response.get('flashcards', []))}")
            return True
        return False

    def test_get_documents(self):
        """Test getting all documents"""
        return self.run_test("Get All Documents", "GET", "documents", 200)

    def test_get_study_materials(self):
        """Test getting study materials for a document"""
        if not self.document_id:
            print("❌ Skipping - No document ID available")
            return False
            
        return self.run_test(
            "Get Study Materials", 
            "GET", 
            f"study-materials/{self.document_id}", 
            200
        )

    def test_chat_endpoint(self):
        """Test the chat endpoint"""
        if not self.document_id:
            print("❌ Skipping - No document ID available")
            return False
            
        chat_data = {
            "document_id": self.document_id,
            "message": "What are the main types of machine learning?"
        }
        
        print("   Sending chat message, waiting for AI response...")
        success, response = self.run_test(
            "Chat with Document", 
            "POST", 
            "chat", 
            200,
            data=chat_data
        )
        
        if success and 'response' in response:
            print(f"   AI Response: {response['response'][:100]}...")
            return True
        return False

    def test_chat_history(self):
        """Test getting chat history"""
        if not self.document_id:
            print("❌ Skipping - No document ID available")
            return False
            
        return self.run_test(
            "Get Chat History", 
            "GET", 
            f"chat-history/{self.document_id}", 
            200
        )

    def test_invalid_endpoints(self):
        """Test error handling with invalid requests"""
        print("\n🔍 Testing Error Handling...")
        
        # Test invalid document ID
        success, _ = self.run_test(
            "Invalid Document ID", 
            "GET", 
            "study-materials/invalid-id", 
            404
        )
        
        # Test chat with invalid document ID
        invalid_chat_data = {
            "document_id": "invalid-id",
            "message": "Test message"
        }
        success2, _ = self.run_test(
            "Chat with Invalid Document ID", 
            "POST", 
            "chat", 
            404,
            data=invalid_chat_data
        )
        
        return success and success2

def main():
    print("🚀 Starting StudyGenie API Tests")
    print("=" * 50)
    
    # Setup
    tester = StudyGenieAPITester()
    
    # Run tests in sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Upload Document", tester.test_upload_document),
        ("Get Documents", tester.test_get_documents),
        ("Get Study Materials", tester.test_get_study_materials),
        ("Chat Endpoint", tester.test_chat_endpoint),
        ("Chat History", tester.test_chat_history),
        ("Error Handling", tester.test_invalid_endpoints),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
            # Add small delay between tests
            time.sleep(1)
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
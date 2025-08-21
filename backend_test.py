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
        """Create a simple PDF-like content for testing"""
        # Create a simple text file that we'll pretend is a PDF
        sample_content = """
        Sample Study Document
        
        Chapter 1: Introduction to Machine Learning
        Machine learning is a subset of artificial intelligence that focuses on algorithms 
        that can learn from data. There are three main types of machine learning:
        
        1. Supervised Learning: Uses labeled data to train models
        2. Unsupervised Learning: Finds patterns in unlabeled data  
        3. Reinforcement Learning: Learns through interaction with environment
        
        Key Concepts:
        - Training Data: The dataset used to train the model
        - Features: Input variables used to make predictions
        - Labels: The target variable we want to predict
        - Overfitting: When a model performs well on training data but poorly on new data
        
        Chapter 2: Neural Networks
        Neural networks are computing systems inspired by biological neural networks.
        They consist of layers of interconnected nodes (neurons) that process information.
        
        Types of Neural Networks:
        - Feedforward Networks: Information flows in one direction
        - Recurrent Networks: Have feedback connections
        - Convolutional Networks: Specialized for processing grid-like data
        """
        
        # For testing purposes, we'll create a simple text file
        # In a real scenario, this would be a proper PDF
        return sample_content.encode('utf-8')

    def test_upload_document(self):
        """Test document upload endpoint"""
        # Create sample PDF content
        pdf_content = self.create_sample_pdf()
        
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
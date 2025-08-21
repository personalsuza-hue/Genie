import requests
import sys
import json
import io
from datetime import datetime
import time
import re

class StudyGenieAPITester:
    def __init__(self, base_url="https://code-fixer-32.preview.emergentagent.com"):
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

    def create_ml_content_pdf(self):
        """Create a PDF with specific machine learning content for testing content-specific generation"""
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
/Length 1200
>>
stream
BT
/F1 12 Tf
100 750 Td
(Machine Learning Fundamentals) Tj
0 -30 Td
(Supervised Learning) Tj
0 -20 Td
(Supervised learning uses labeled training data to learn a mapping) Tj
0 -15 Td
(from input features to target outputs. Common algorithms include:) Tj
0 -15 Td
(- Linear Regression: predicts continuous values) Tj
0 -15 Td
(- Logistic Regression: binary classification) Tj
0 -15 Td
(- Decision Trees: hierarchical decision making) Tj
0 -15 Td
(- Random Forest: ensemble of decision trees) Tj
0 -15 Td
(- Support Vector Machines: finds optimal decision boundary) Tj
0 -30 Td
(Unsupervised Learning) Tj
0 -20 Td
(Unsupervised learning finds patterns in data without labels:) Tj
0 -15 Td
(- K-Means Clustering: groups similar data points) Tj
0 -15 Td
(- Hierarchical Clustering: creates tree of clusters) Tj
0 -15 Td
(- Principal Component Analysis: dimensionality reduction) Tj
0 -15 Td
(- DBSCAN: density-based clustering algorithm) Tj
0 -30 Td
(Key Concepts) Tj
0 -20 Td
(Overfitting: model memorizes training data, poor generalization) Tj
0 -15 Td
(Underfitting: model too simple, high bias) Tj
0 -15 Td
(Cross-validation: technique to assess model performance) Tj
0 -15 Td
(Feature Engineering: creating relevant input variables) Tj
0 -15 Td
(Regularization: prevents overfitting by adding penalty terms) Tj
0 -15 Td
(Gradient Descent: optimization algorithm for training) Tj
0 -15 Td
(Bias-Variance Tradeoff: balance between model complexity) Tj
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
1605
%%EOF"""
        return pdf_content

    def test_content_specific_generation(self):
        """Test that AI generates content-specific MCQs and flashcards, not generic ones"""
        print("\n🎯 Testing Content-Specific AI Generation...")
        
        # Upload ML content PDF
        ml_pdf_content = self.create_ml_content_pdf()
        files = {
            'file': ('ml_fundamentals.pdf', io.BytesIO(ml_pdf_content), 'application/pdf')
        }
        
        success, response = self.run_test(
            "Upload ML Content PDF", 
            "POST", 
            "upload", 
            200,
            files=files
        )
        
        if not success or 'document_id' not in response:
            print("❌ Failed to upload ML content PDF")
            return False
            
        self.document_id = response['document_id']
        mcqs = response.get('mcqs', [])
        flashcards = response.get('flashcards', [])
        
        print(f"   Generated {len(mcqs)} MCQs and {len(flashcards)} flashcards")
        
        # Test MCQ content specificity
        mcq_specific = self.analyze_mcq_specificity(mcqs)
        flashcard_specific = self.analyze_flashcard_specificity(flashcards)
        
        # Test chat context awareness
        chat_specific = self.test_chat_context_awareness()
        
        return mcq_specific and flashcard_specific and chat_specific

    def analyze_mcq_specificity(self, mcqs):
        """Analyze if MCQs are content-specific rather than generic"""
        print("\n   🔍 Analyzing MCQ Content Specificity...")
        
        if not mcqs:
            print("   ❌ No MCQs generated")
            return False
            
        # Define ML-specific terms that should appear in content-specific questions
        ml_terms = [
            'supervised', 'unsupervised', 'overfitting', 'underfitting', 
            'regression', 'classification', 'clustering', 'decision tree',
            'random forest', 'svm', 'support vector', 'k-means', 'pca',
            'cross-validation', 'gradient descent', 'regularization',
            'bias', 'variance', 'feature engineering', 'dbscan'
        ]
        
        # Generic fallback indicators
        generic_indicators = [
            'topic a', 'topic b', 'topic c', 'topic d',
            'option a', 'option b', 'option c', 'option d',
            'sample question', 'main topic', 'key concept',
            'based on the uploaded content', 'document content analysis'
        ]
        
        specific_count = 0
        generic_count = 0
        
        for i, mcq in enumerate(mcqs):
            question_text = mcq.get('question', '').lower()
            options_text = ' '.join(mcq.get('options', [])).lower()
            explanation_text = mcq.get('explanation', '').lower()
            full_text = f"{question_text} {options_text} {explanation_text}"
            
            print(f"   MCQ {i+1}: {mcq.get('question', 'No question')[:80]}...")
            
            # Check for ML-specific terms
            has_ml_terms = any(term in full_text for term in ml_terms)
            
            # Check for generic indicators
            has_generic = any(indicator in full_text for indicator in generic_indicators)
            
            if has_ml_terms and not has_generic:
                specific_count += 1
                print(f"      ✅ Content-specific (contains ML terms)")
            elif has_generic:
                generic_count += 1
                print(f"      ❌ Generic fallback detected")
            else:
                print(f"      ⚠️  Unclear specificity")
        
        specificity_ratio = specific_count / len(mcqs) if mcqs else 0
        print(f"   📊 MCQ Specificity: {specific_count}/{len(mcqs)} ({specificity_ratio:.1%}) are content-specific")
        
        # Require at least 70% of MCQs to be content-specific
        if specificity_ratio >= 0.7:
            print("   ✅ MCQs are sufficiently content-specific")
            return True
        else:
            print("   ❌ Too many generic MCQs detected")
            return False

    def analyze_flashcard_specificity(self, flashcards):
        """Analyze if flashcards are content-specific rather than generic"""
        print("\n   🔍 Analyzing Flashcard Content Specificity...")
        
        if not flashcards:
            print("   ❌ No flashcards generated")
            return False
            
        # ML-specific terms for flashcards
        ml_terms = [
            'supervised learning', 'unsupervised learning', 'overfitting', 'underfitting',
            'linear regression', 'logistic regression', 'decision tree', 'random forest',
            'support vector machine', 'k-means', 'clustering', 'pca', 'principal component',
            'cross-validation', 'gradient descent', 'regularization', 'bias-variance',
            'feature engineering', 'dbscan', 'hierarchical clustering'
        ]
        
        # Generic fallback indicators
        generic_indicators = [
            'key concept from the document', 'main topic', 'summary of the document',
            'definition or explanation based on the content', 'concept from document'
        ]
        
        specific_count = 0
        generic_count = 0
        
        for i, card in enumerate(flashcards):
            front_text = card.get('front', '').lower()
            back_text = card.get('back', '').lower()
            full_text = f"{front_text} {back_text}"
            
            print(f"   Card {i+1}: {card.get('front', 'No front')[:50]}...")
            
            # Check for ML-specific terms
            has_ml_terms = any(term in full_text for term in ml_terms)
            
            # Check for generic indicators
            has_generic = any(indicator in full_text for indicator in generic_indicators)
            
            if has_ml_terms and not has_generic:
                specific_count += 1
                print(f"      ✅ Content-specific (contains ML terms)")
            elif has_generic:
                generic_count += 1
                print(f"      ❌ Generic fallback detected")
            else:
                print(f"      ⚠️  Unclear specificity")
        
        specificity_ratio = specific_count / len(flashcards) if flashcards else 0
        print(f"   📊 Flashcard Specificity: {specific_count}/{len(flashcards)} ({specificity_ratio:.1%}) are content-specific")
        
        # Require at least 70% of flashcards to be content-specific
        if specificity_ratio >= 0.7:
            print("   ✅ Flashcards are sufficiently content-specific")
            return True
        else:
            print("   ❌ Too many generic flashcards detected")
            return False

    def test_chat_context_awareness(self):
        """Test that chat responses are contextually relevant to the document"""
        print("\n   🔍 Testing Chat Context Awareness...")
        
        if not self.document_id:
            print("   ❌ No document ID available")
            return False
        
        # Test questions that should have specific answers based on the ML content
        test_questions = [
            "What is overfitting?",
            "Name three supervised learning algorithms mentioned in the document",
            "What is the difference between supervised and unsupervised learning?",
            "What clustering algorithms are discussed?"
        ]
        
        context_aware_responses = 0
        
        for question in test_questions:
            chat_data = {
                "document_id": self.document_id,
                "message": question
            }
            
            print(f"   Testing: {question}")
            success, response = self.run_test(
                f"Chat Context Test", 
                "POST", 
                "chat", 
                200,
                data=chat_data
            )
            
            if success and 'response' in response:
                ai_response = response['response'].lower()
                print(f"      Response: {response['response'][:100]}...")
                
                # Check if response contains relevant ML terms
                relevant_terms = [
                    'supervised', 'unsupervised', 'overfitting', 'training data',
                    'regression', 'classification', 'clustering', 'decision tree',
                    'random forest', 'k-means', 'pca', 'regularization'
                ]
                
                has_relevant_content = any(term in ai_response for term in relevant_terms)
                
                # Check for generic non-answers
                generic_responses = [
                    "i don't have information", "not mentioned in the document",
                    "i cannot find", "not available in the provided content"
                ]
                
                is_generic = any(generic in ai_response for generic in generic_responses)
                
                if has_relevant_content and not is_generic:
                    context_aware_responses += 1
                    print(f"      ✅ Context-aware response")
                else:
                    print(f"      ❌ Generic or irrelevant response")
            
            time.sleep(1)  # Rate limiting
        
        awareness_ratio = context_aware_responses / len(test_questions)
        print(f"   📊 Chat Context Awareness: {context_aware_responses}/{len(test_questions)} ({awareness_ratio:.1%}) responses were context-aware")
        
        if awareness_ratio >= 0.75:
            print("   ✅ Chat responses are sufficiently context-aware")
            return True
        else:
            print("   ❌ Chat responses lack sufficient context awareness")
            return False

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
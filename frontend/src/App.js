import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { Upload, MessageCircle, FileText, Brain, Sparkles, BookOpen } from "lucide-react";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Badge } from "./components/ui/badge";
import { ScrollArea } from "./components/ui/scroll-area";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [document, setDocument] = useState(null);
  const [mcqs, setMcqs] = useState([]);
  const [flashcards, setFlashcards] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [isChatting, setIsChatting] = useState(false);
  const [currentFlashcard, setCurrentFlashcard] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [quizMode, setQuizMode] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);

  const handleFileUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setDocument(response.data);
      setMcqs(response.data.mcqs || []);
      setFlashcards(response.data.flashcards || []);
      setChatMessages([]);
    } catch (error) {
      console.error("Upload error:", error);
      alert("Error uploading file. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !document) return;

    setIsChatting(true);
    const userMessage = newMessage;
    setNewMessage("");

    // Add user message to chat
    setChatMessages(prev => [...prev, { type: "user", message: userMessage }]);

    try {
      const response = await axios.post(`${API}/chat`, {
        document_id: document.document_id,
        message: userMessage,
      });

      // Add AI response to chat
      setChatMessages(prev => [...prev, { type: "ai", message: response.data.response }]);
    } catch (error) {
      console.error("Chat error:", error);
      setChatMessages(prev => [...prev, { type: "ai", message: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setIsChatting(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const nextFlashcard = () => {
    setShowAnswer(false);
    setCurrentFlashcard((prev) => (prev + 1) % flashcards.length);
  };

  const prevFlashcard = () => {
    setShowAnswer(false);
    setCurrentFlashcard((prev) => (prev - 1 + flashcards.length) % flashcards.length);
  };

  const startQuiz = () => {
    setQuizMode(true);
    setCurrentQuestion(0);
    setSelectedAnswer(null);
    setShowResult(false);
    setScore(0);
  };

  const selectAnswer = (answerIndex) => {
    setSelectedAnswer(answerIndex);
  };

  const submitAnswer = () => {
    if (selectedAnswer === null) return;

    const isCorrect = selectedAnswer === mcqs[currentQuestion].correct_answer;
    if (isCorrect) {
      setScore(prev => prev + 1);
    }

    setShowResult(true);
    setTimeout(() => {
      if (currentQuestion + 1 < mcqs.length) {
        setCurrentQuestion(prev => prev + 1);
        setSelectedAnswer(null);
        setShowResult(false);
      } else {
        // Quiz completed
        alert(`Quiz completed! Your score: ${score + (isCorrect ? 1 : 0)}/${mcqs.length}`);
        setQuizMode(false);
      }
    }, 2000);
  };

  if (!document) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
        <div className="container mx-auto px-4 py-16">
          {/* Hero Section */}
          <div className="text-center mb-16">
            <div className="flex justify-center items-center mb-6">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 rounded-2xl shadow-lg">
                <Brain className="h-12 w-12 text-white" />
              </div>
            </div>
            <h1 className="text-6xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-6">
              StudyGenie
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
              Transform your learning materials into interactive study tools with AI. 
              Upload a PDF and get instant quizzes, flashcards, and a smart tutor.
            </p>
            
            {/* Features Grid */}
            <div className="grid md:grid-cols-3 gap-8 mb-12 max-w-4xl mx-auto">
              <div className="bg-white p-6 rounded-xl shadow-sm border">
                <FileText className="h-8 w-8 text-indigo-600 mx-auto mb-4" />
                <h3 className="font-semibold text-gray-900 mb-2">Smart Quiz Generation</h3>
                <p className="text-gray-600 text-sm">AI creates multiple-choice questions from your documents</p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-sm border">
                <BookOpen className="h-8 w-8 text-purple-600 mx-auto mb-4" />
                <h3 className="font-semibold text-gray-900 mb-2">Interactive Flashcards</h3>
                <p className="text-gray-600 text-sm">Automatically generated flashcards for effective memorization</p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-sm border">
                <MessageCircle className="h-8 w-8 text-cyan-600 mx-auto mb-4" />
                <h3 className="font-semibold text-gray-900 mb-2">AI Tutor Chat</h3>
                <p className="text-gray-600 text-sm">Ask questions and get answers based on your document</p>
              </div>
            </div>
          </div>

          {/* Upload Section */}
          <Card className="max-w-md mx-auto shadow-lg">
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-600" />
                Get Started
              </CardTitle>
              <CardDescription>
                Upload a PDF document to generate study materials
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-indigo-200 rounded-lg p-8 text-center hover:border-indigo-300 transition-colors">
                <Upload className="h-12 w-12 text-indigo-400 mx-auto mb-4" />
                <Input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setFile(e.target.files[0])}
                  className="mb-4"
                />
                {file && (
                  <p className="text-sm text-gray-600 mb-4">
                    Selected: {file.name}
                  </p>
                )}
              </div>
              <Button
                onClick={handleFileUpload}
                disabled={!file || isUploading}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
              >
                {isUploading ? "Processing..." : "Upload & Generate Study Materials"}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
            StudyGenie
          </h1>
          <p className="text-gray-600">
            Study materials for: <span className="font-semibold">{document.filename}</span>
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.location.reload()}
            className="mt-2"
          >
            Upload New Document
          </Button>
        </div>

        <Tabs defaultValue="quiz" className="max-w-6xl mx-auto">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="quiz" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Quiz
            </TabsTrigger>
            <TabsTrigger value="flashcards" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Flashcards
            </TabsTrigger>
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              AI Tutor
            </TabsTrigger>
          </TabsList>

          {/* Quiz Tab */}
          <TabsContent value="quiz">
            <Card>
              <CardHeader>
                <CardTitle>Interactive Quiz</CardTitle>
                <CardDescription>
                  Test your knowledge with AI-generated questions
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!quizMode ? (
                  <div className="text-center py-8">
                    <p className="text-gray-600 mb-4">
                      Ready to test your knowledge? This quiz has {mcqs.length} questions.
                    </p>
                    <Button onClick={startQuiz} className="bg-indigo-600 hover:bg-indigo-700">
                      Start Quiz
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="flex justify-between items-center">
                      <Badge variant="outline">
                        Question {currentQuestion + 1} of {mcqs.length}
                      </Badge>
                      <Badge variant="outline">
                        Score: {score}/{mcqs.length}
                      </Badge>
                    </div>
                    
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <h3 className="text-lg font-semibold mb-4">
                        {mcqs[currentQuestion]?.question}
                      </h3>
                      
                      <div className="space-y-3">
                        {mcqs[currentQuestion]?.options.map((option, index) => (
                          <button
                            key={index}
                            onClick={() => selectAnswer(index)}
                            disabled={showResult}
                            className={`w-full p-3 text-left rounded-lg border transition-colors ${
                              selectedAnswer === index
                                ? showResult
                                  ? index === mcqs[currentQuestion].correct_answer
                                    ? "bg-green-100 border-green-500 text-green-800"
                                    : "bg-red-100 border-red-500 text-red-800"
                                  : "bg-indigo-100 border-indigo-500"
                                : showResult && index === mcqs[currentQuestion].correct_answer
                                ? "bg-green-100 border-green-500 text-green-800"
                                : "bg-white border-gray-200 hover:border-gray-300"
                            }`}
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                      
                      {showResult && (
                        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                          <p className="text-sm text-blue-800">
                            <strong>Explanation:</strong> {mcqs[currentQuestion]?.explanation}
                          </p>
                        </div>
                      )}
                    </div>
                    
                    {!showResult && (
                      <Button
                        onClick={submitAnswer}
                        disabled={selectedAnswer === null}
                        className="w-full"
                      >
                        Submit Answer
                      </Button>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Flashcards Tab */}
          <TabsContent value="flashcards">
            <Card>
              <CardHeader>
                <CardTitle>Study Flashcards</CardTitle>
                <CardDescription>
                  Review key concepts with interactive flashcards
                </CardDescription>
              </CardHeader>
              <CardContent>
                {flashcards.length > 0 ? (
                  <div className="space-y-6">
                    <div className="text-center">
                      <Badge variant="outline">
                        Card {currentFlashcard + 1} of {flashcards.length}
                      </Badge>
                    </div>
                    
                    <div
                      className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-8 rounded-xl min-h-[200px] flex items-center justify-center cursor-pointer transform transition-transform hover:scale-105"
                      onClick={() => setShowAnswer(!showAnswer)}
                    >
                      <div className="text-center">
                        <p className="text-lg mb-4">
                          {showAnswer ? flashcards[currentFlashcard]?.back : flashcards[currentFlashcard]?.front}
                        </p>
                        <p className="text-sm opacity-75">
                          Click to {showAnswer ? "show question" : "reveal answer"}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex justify-between">
                      <Button variant="outline" onClick={prevFlashcard}>
                        Previous
                      </Button>
                      <Button variant="outline" onClick={nextFlashcard}>
                        Next
                      </Button>
                    </div>
                  </div>
                ) : (
                  <p className="text-center text-gray-600">No flashcards available</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Chat Tab */}
          <TabsContent value="chat">
            <Card>
              <CardHeader>
                <CardTitle>AI Tutor Chat</CardTitle>
                <CardDescription>
                  Ask questions about your document and get instant answers
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <ScrollArea className="h-96 border rounded-lg p-4">
                    {chatMessages.length === 0 ? (
                      <div className="text-center text-gray-500 py-8">
                        <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Start a conversation! Ask me anything about your document.</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {chatMessages.map((msg, index) => (
                          <div
                            key={index}
                            className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
                          >
                            <div
                              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                                msg.type === "user"
                                  ? "bg-indigo-600 text-white"
                                  : "bg-gray-100 text-gray-800"
                              }`}
                            >
                              {msg.message}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>
                  
                  <div className="flex gap-2">
                    <Input
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask a question about your document..."
                      disabled={isChatting}
                    />
                    <Button
                      onClick={sendMessage}
                      disabled={!newMessage.trim() || isChatting}
                    >
                      {isChatting ? "..." : "Send"}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;
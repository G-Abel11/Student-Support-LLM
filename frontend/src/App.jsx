// frontend/src/App.jsx

import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  // State variables — React re-renders the UI whenever these change
  const [question, setQuestion] = useState("");   // what the user typed
  const [answer, setAnswer] = useState("");       // the LLM's response
  const [loading, setLoading] = useState(false);  // spinner on/off
  const [error, setError] = useState("");         // error message if any

  const handleSubmit = async () => {
    // Error handling — empty question
    if (!question.trim()) {
      setError("Please enter a question before submitting.");
      return;
    }

    // Reset previous state
    setError("");
    setAnswer("");
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/ask`, {
        question: question,
      });
      setAnswer(response.data.answer);

    } catch (err) {
      // Backend is not running
      if (err.code === "ERR_NETWORK") {
        setError("Cannot connect to the server. Please ensure the backend is running.");
      }
      // Backend returned an error (e.g. Ollama down)
      else if (err.response) {
        setError(`Server error: ${err.response.data.detail}`);
      }
      else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setLoading(false); // always stop spinner whether success or error
    }
  };

  // Allow pressing Enter to submit
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !loading) handleSubmit();
  };

  return (
    <div className="container">

      {/* Header */}
      <div className="header">
        <h1>University Student Support Assistant</h1>
        <p>Ask me anything about university services</p>
      </div>

      {/* Topics */}
      <div className="topics">
        {["Course Registration", "Exam Rules", "Library Services",
          "ICT Support", "Hostel Application", "Fee Payment",
          "Academic Calendar", "Student Conduct"].map((topic) => (
          <span
            key={topic}
            className="topic-tag"
            onClick={() => setQuestion(`Tell me about ${topic}`)}
          >
            {topic}
          </span>
        ))}
      </div>

      {/* Input area */}
      <div className="input-area">
        <textarea
          className="question-input"
          placeholder="Type your question here... e.g. How do I register for courses?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={3}
          disabled={loading}
        />
        <button
          className={`submit-btn ${loading ? "loading" : ""}`}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="error-box">
          <span>⚠ {error}</span>
        </div>
      )}

      {/* Loading spinner */}
      {loading && (
        <div className="loading-box">
          <div className="spinner"></div>
          <span>The assistant is thinking, please wait...</span>
        </div>
      )}

      {/* Answer */}
      {answer && !loading && (
        <div className="answer-box">
          <h3>Answer</h3>
          <p>{answer}</p>
        </div>
      )}

    </div>
  );
}

export default App;
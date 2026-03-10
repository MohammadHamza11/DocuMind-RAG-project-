import React, { useState, useRef, useEffect } from "react";
import FileUpload from "./components/FileUpload";
import ChatMessage from "./components/ChatMessage";
import DocumentList from "./components/DocumentList";
import { uploadDocument, queryDocuments, listDocuments, deleteAllDocuments } from "./api";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [documents, setDocuments] = useState([]);
  const messagesEndRef = useRef(null);

  // Fetch indexed documents on mount
  useEffect(() => {
    refreshDocuments();
  }, []);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const refreshDocuments = async () => {
    try {
      const data = await listDocuments();
      setDocuments(data.documents);
    } catch {
      // silently ignore on initial load
    }
  };

  const handleUpload = async (file) => {
    setUploading(true);
    setUploadStatus({ type: "loading", text: `Uploading ${file.name}...` });
    try {
      const result = await uploadDocument(file);
      setUploadStatus({ type: "success", text: result.message });
      refreshDocuments();
    } catch (err) {
      const detail = err.response?.data?.detail || "Upload failed.";
      setUploadStatus({ type: "error", text: detail });
    } finally {
      setUploading(false);
    }
  };

  const handleClearDocuments = async () => {
    try {
      await deleteAllDocuments();
      setDocuments([]);
      setMessages([]);
      setUploadStatus(null);
    } catch {
      setUploadStatus({ type: "error", text: "Failed to clear documents." });
    }
  };

  const handleSend = async () => {
    const question = input.trim();
    if (!question || loading) return;

    const userMsg = { role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // Build chat history (exclude sources for API)
      const chatHistory = [...messages, userMsg].map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const data = await queryDocuments(question, chatHistory);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="app">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <h1>DocuMind</h1>
        <p className="tagline">RAG-Powered Document Q&A</p>

        <FileUpload onUpload={handleUpload} uploading={uploading} />

        {uploadStatus && (
          <div className={`upload-status ${uploadStatus.type}`}>
            {uploadStatus.text}
          </div>
        )}

        <DocumentList documents={documents} onClear={handleClearDocuments} />
      </aside>

      {/* ── Chat ── */}
      <main className="chat-area">
        <div className="chat-header">Chat with your Documents</div>

        <div className="messages">
          {messages.length === 0 ? (
            <div className="welcome">
              <h2>Welcome to DocuMind</h2>
              <p>
                Upload PDF or DOCX documents using the sidebar, then ask
                questions about their content. Answers will include inline
                source citations.
              </p>
            </div>
          ) : (
            messages.map((msg, idx) => <ChatMessage key={idx} message={msg} />)
          )}
          {loading && (
            <div className="message assistant">
              <div className="thinking">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-bar">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            disabled={loading}
          />
          <button
            className="send-btn"
            onClick={handleSend}
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </main>
    </div>
  );
}

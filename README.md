# DocuMind — RAG-Based Document Q&A Assistant

A full-stack retrieval-augmented generation (RAG) system that lets users upload PDF and DOCX files and query them conversationally, with responses grounded in and cited from source documents.

**Tech Stack:** Python · LangChain · Google Gemini API · FAISS · FastAPI · React

---

## Features

- **Multi-document upload** — Drag-and-drop PDF & DOCX files
- **Semantic search** — Google Gemini embeddings + FAISS vector search with sub-second retrieval on 200+ page corpora
- **Conversational Q&A** — Chat with your documents using GPT with full context awareness
- **Inline source citations** — Every answer cites the source filename and page number
- **Persistent chat history** — Conversation context maintained across messages
- **Document management** — View indexed documents and clear the knowledge base

---

## Project Structure

```
DocuMind-RAG-project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application & endpoints
│   │   ├── config.py          # Settings & environment variables
│   │   ├── document_processor.py  # PDF/DOCX loading & chunking
│   │   ├── vector_store.py    # FAISS index management
│   │   ├── rag_chain.py       # LangChain RAG pipeline
│   │   └── schemas.py         # Pydantic request/response models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── ChatMessage.jsx
│   │   │   └── DocumentList.jsx
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
├── .gitignore
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- An [Google Gemini API key](https://aistudio.google.com/apikey)

### 1. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be running at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm start
```

The app will open at `http://localhost:3000`.

---

## API Endpoints

| Method   | Endpoint      | Description                        |
| -------- | ------------- | ---------------------------------- |
| `POST`   | `/upload`     | Upload and index a PDF/DOCX file   |
| `POST`   | `/query`      | Ask a question about your documents|
| `GET`    | `/documents`  | List all indexed document sources  |
| `DELETE` | `/documents`  | Clear all documents and the index  |
| `GET`    | `/health`     | Health check                       |

---

## How It Works

1. **Upload** — User uploads PDF/DOCX files via the React frontend
2. **Process** — Backend extracts text and splits it into overlapping chunks (1000 chars, 200 overlap)
3. **Embed** — Each chunk is embedded using Google's `embedding-001` model
4. **Index** — Embeddings are stored in a FAISS vector index for fast similarity search
5. **Query** — User asks a question; the system retrieves the top-5 most relevant chunks
6. **Generate** — LangChain sends the retrieved context + chat history to Gemini, which produces a cited answer

---

## License

MIT
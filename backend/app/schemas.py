"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class QueryRequest(BaseModel):
    question: str
    chat_history: list[ChatMessage] = []


class SourceCitation(BaseModel):
    source: str
    page: int | str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str


class DocumentInfo(BaseModel):
    filename: str


class DocumentListResponse(BaseModel):
    documents: list[str]

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    google_api_key: str = ""
    embedding_model: str = "models/gemini-embedding-001"
    chat_model: str = "gemini-2.5-flash"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    upload_dir: Path = Path(__file__).parent.parent / "uploads"
    vector_store_dir: Path = Path(__file__).parent.parent / "vector_store"

    class Config:
        env_file = ".env"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.vector_store_dir.mkdir(parents=True, exist_ok=True)

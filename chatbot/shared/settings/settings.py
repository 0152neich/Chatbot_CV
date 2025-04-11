from __future__ import annotations

from dotenv import find_dotenv
from dotenv import load_dotenv

from pydantic_settings import BaseSettings

from .models.embedding import EmbeddingSettings
from .models.chunking import ChunkSettings
from .models.qdrant import QdantSettings
from .models.generation import GenerationSettings
from .models.retrieval import RetrevalSettings

load_dotenv(find_dotenv('.env'), override=True)

class Settings(BaseSettings):
    chunking: ChunkSettings
    embedding: EmbeddingSettings
    qdrant: QdantSettings
    generation: GenerationSettings
    retrieval: RetrevalSettings

    class Config:
        env_nested_delimiter = '__'

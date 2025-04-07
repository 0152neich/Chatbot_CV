from __future__ import annotations

from shared.base import BaseModel

class EmbeddingSettings(BaseModel):
    dense_model_path: str
    sparse_model_path: str
    max_token_limit: int

from __future__ import annotations

from shared.base import BaseModel

class GenerationSettings(BaseModel):
    """Settings for the generation model."""
    model: str
    temperature: float
    max_tokens: int
    api_key: str

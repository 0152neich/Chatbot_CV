from __future__ import annotations

from shared.base import BaseModel

class ChunkSettings(BaseModel):
    chunk_size: int
    chunk_overlap: int

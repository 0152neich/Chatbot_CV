from __future__ import annotations

from shared.base import BaseModel

class IndexingSettings(BaseModel):
    raw_path: str
    convert_path: str
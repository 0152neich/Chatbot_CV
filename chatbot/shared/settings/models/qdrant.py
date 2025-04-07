from __future__ import annotations

from shared.base import BaseModel

class QdantSettings(BaseModel):
    url:str
    port:int
    name:str
    vector_size:int

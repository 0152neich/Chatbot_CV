from __future__ import annotations

from shared.base import BaseModel

class APIInput(BaseModel):
    query: str
    user_name: str

class APIOutput(BaseModel):
    response: str
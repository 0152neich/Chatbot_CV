from typing import List
from shared.base import BaseModel

class SparseEmbeddingData(BaseModel):
    indices: List[int]
    values: List[float]
from typing import List, Dict, Any

from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings
from shared.sparse_embedding import SparseEmbeddingData
from infrastructure.qdrant import Qdrant


class RetrievalInput(BaseModel):
    dense_query: List[float]
    sparse_query: List[SparseEmbeddingData]
    user_name: str

class RetrievalOutput(BaseModel):
    context: List[Dict[str, Any]]

class RetrievalService(BaseService):
    settings: Settings

    @property
    def _get_qdrant(self) -> Qdrant:
        return Qdrant(settings=self.settings)

    def process(self, inputs: RetrievalInput) -> RetrievalOutput:
        """Retrieve documents from the database based on the query.

        Args:
            input (RetrievalInput): Input data containing the query and optional parameters.

        Returns:
            RetrievalOutput: Output data containing the retrieved documents and metadata.
        """
        qdrant_outputs = self._get_qdrant.query(
            dense_query=inputs.dense_query,
            sparse_query=inputs.sparse_query,
            user_name=inputs.user_name,
            k=self.settings.retrieval.top_k,
        )
        
        context = list(qdrant_output.payload for qdrant_output in qdrant_outputs.points)
        return RetrievalOutput(context=context)
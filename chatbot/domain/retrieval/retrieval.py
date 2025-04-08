from typing import List, Dict, Any

from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings
from shared.qdrant import Qdrant
from shared.sparse_embedding import SparseEmbeddingData

class RetrievalInput(BaseModel):
    dense_query: List[Dict]
    sparse_query: List[SparseEmbeddingData]
    n_results: int
    filters: Dict[str, Any]

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
            metadata=inputs.filters,
            k=inputs.n_results
        )
        
        context = list(qdrant_output.payload for qdrant_output in qdrant_outputs.points)
        return RetrievalOutput(context=context)
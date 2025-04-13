import logging
from functools import cached_property
from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings

from .indexing import IndexingService
from domain.retrieval import RetrievalService
from domain.retrieval import RetrievalInput
from domain.generation import GenerationService
from domain.generation import GenerationInput
from domain.indexing import EmbeddingService
from domain.indexing import EmbeddingInput
from infrastructure.qdrant import Qdrant

logger = logging.getLogger(__name__)

class ChatbotInput(BaseModel):
    query: str
    user_name: str

class ChatbotOutput(BaseModel):
    response: str

class ChatbotService(BaseService):
    settings: Settings

    @property
    def _get_indexing(self) -> IndexingService:
        return IndexingService(settings=self.settings)

    @property
    def _get_retrieval(self) -> RetrievalService:
        return RetrievalService(settings=self.settings)
    
    @property
    def _get_generation(self) -> GenerationService:
        return GenerationService(settings=self.settings)

    @cached_property
    def _get_qdrant(self) -> Qdrant:
        return Qdrant(settings=self.settings)
    
    @cached_property
    def _get_embedding(self) -> EmbeddingService:
        return EmbeddingService(settings=self.settings)
    
    def process(self, inputs: ChatbotInput) -> ChatbotOutput:
        """ Generate a response based on the input query.

        Args:
            inputs (ChatbotInput): Input data containing the query.

        Returns:
            ChatbotOutput: Output data containing the generated response.
        """
        try:
            embedding_query = self._get_embedding.process(
                EmbeddingInput(
                    chunk=[],
                    query=inputs.query
                )
            )
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise e

        try:
            retrieval_output = self._get_retrieval.process(
                RetrievalInput(
                    dense_query=embedding_query.dense_embeddings[0],
                    sparse_query=embedding_query.sparse_embeddings,
                    user_name=inputs.user_name,
                )
            )
            logger.info("Information retrieved successfully.")
            if not retrieval_output.context:
                return ChatbotOutput(response="Không tìm thấy thông tin liên quan. Bạn có muốn hỏi câu khác không?")
        except Exception as e:
            logger.error(f"Error retrieving information: {e}")
            raise e
        
        try:
            generation_output = self._get_generation.process(
                GenerationInput(
                    query=inputs.query,
                    chat_history=[],
                    retrieved_info=retrieval_output.context
                )
            )
            logger.info("Response generated successfully.")
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise e
        
        return ChatbotOutput(response=generation_output.response)
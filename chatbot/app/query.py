import logging
from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings

from .indexing import IndexingService
from domain.retrieval import RetrievalService
from domain.generation import GenerationService
from domain.generation import GenerationInput
from infrastructure.qdrant import Qdrant

logger = logging.getLogger(__name__)

class ChatbotInput(BaseModel):
    query: str

class ChatbotOutput(BaseModel):
    response: str

class ChatbotService(BaseService):
    settings: Settings

    @property
    def _get_indexing(self) -> IndexingService:
        return IndexingService(setting=self.settings)

    @property
    def _get_retrieval(self) -> RetrievalService:
        return RetrievalService(setting=self.settings)
    
    @property
    def _get_generation(self) -> GenerationService:
        return GenerationService(setting=self.settings)

    @property
    def _get_qdrant(self) -> Qdrant:
        return Qdrant(setting=self.settings)
    
    def process(self, inputs: ChatbotInput) -> ChatbotOutput:
        """ Generate a response based on the input query.

        Args:
            inputs (ChatbotInput): Input data containing the query.

        Returns:
            ChatbotOutput: Output data containing the generated response.
        """
        try:
            retrieval_output = self._get_retrieval.process(inputs.query)
            logger.info("Information retrieved successfully.")
        except Exception as e:
            logger.error(f"Error retrieving information: {e}")
            raise e
        
        try:
            generation_output = self._get_generation.process(
                GenerationInput(
                    query=inputs.query,
                    chat_history=retrieval_output.context,
                    retrieved_info=retrieval_output.context
                )
            )
            logger.info("Response generated successfully.")
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise e
        
        return ChatbotOutput(response=generation_output.response)
        

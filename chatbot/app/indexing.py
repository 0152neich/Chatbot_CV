import logging

from domain.indexing import EmbeddingService
from domain.indexing import EmbeddingInput
from domain.indexing import Chunker
from domain.indexing import DocumentProcessor

from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings
from infrastructure.qdrant import Qdrant
from infrastructure.qdrant import QdrantInput

logger = logging.getLogger(__name__)

class IndexingOutput(BaseModel):
    status: bool

class IndexingService(BaseService):
    settings: Settings

    @property
    def _get_convert(self) -> DocumentProcessor:
        return DocumentProcessor()
    
    @property
    def _get_chunker(self) -> Chunker:
        return Chunker(settings=self.settings)
    
    @property
    def _get_embedding(self) -> EmbeddingService:
        return EmbeddingService(settings=self.settings)
    
    @property
    def _get_qdrant(self) -> Qdrant:
        return Qdrant(settings=self.settings)
    
    def process(self) -> IndexingOutput:
        """Process the input file and return the indexing output.
        
        Args:
            inputs (IndexingInput): Input file path.
        
        Returns:
            IndexingOutput: Indexing output.
        """
        # Convert the file to text
        try:
            text = self._get_convert.process_all()
            logger.info("File converted to text successfully.")
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            raise e
        
        # Chunk the text
        try:
            chunks_output = self._get_chunker.process()
            logger.info("Text chunked successfully.")
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise e
        
        # Embed the chunks
        try:
            embeddings = self._get_embedding.process(EmbeddingInput(chunks=chunks_output.chunks))
            logger.info("Chunks embedded successfully.")
        except Exception as e:
            logger.error(f"Error embedding chunks: {e}")
            raise e

        # Store the embeddings in Qdrant
        try:
            self._get_qdrant.insert(
                QdrantInput(    
                    dense_embeddings=embeddings.dense_embeddings,
                    sparse_embeddings=embeddings.sparse_embeddings,
                    metadata=embeddings.metadata
                )
            )
            logger.info("Embeddings stored successfully.")
            return IndexingOutput(status=True)
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            raise e
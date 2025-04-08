import logging

from infrastructure.indexing import EmbeddingService
from infrastructure.indexing import EmbeddingInput
from infrastructure.indexing import Chunker
from infrastructure.indexing import ChunkInput
from infrastructure.indexing import DocumentProcessor

from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings
from shared.qdrant import Qdrant
from shared.qdrant import QdrantInput

logger = logging.getLogger(__name__)

class IndexingOutput(BaseModel):
    status: bool

class IndexingService(BaseService):
    setting: Settings

    @property
    def _get_convert(self) -> DocumentProcessor:
        return DocumentProcessor()
    
    @property
    def _get_chunker(self) -> Chunker:
        return Chunker(setting=self.setting)
    
    @property
    def _get_embedding(self) -> EmbeddingService:
        return EmbeddingService(setting=self.setting)
    
    @property
    def _get_qdrant(self) -> Qdrant:
        return Qdrant(setting=self.setting)
    
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
                    payload=embeddings.metadata
                )
            )
            logger.info("Embeddings stored successfully.")
            return IndexingOutput(status=True)
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            raise e
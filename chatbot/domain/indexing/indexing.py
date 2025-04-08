import logging

from infrastructure.indexing import EmbeddingService
from infrastructure.indexing import EmbeddingInput
from infrastructure.indexing import Chunker
from infrastructure.indexing import ChunkInput
from infrastructure.indexing import DocumentProcessor

from shared.base import BaseModel
from shared.base import BaseService
from shared.sparse_embedding import SparseEmbeddingData
from shared.settings import Settings

logger = logging.getLogger(__name__)

class IndexingInput(BaseModel):
    file_path: str

class IndexingOutput(BaseModel):
    dense_embeddings: list[float]
    sparse_embeddings: list[SparseEmbeddingData]

class IndexingService(BaseService):
    setting: Settings

    def _get_convert(self) -> DocumentProcessor:
        return DocumentProcessor()
    
    def _get_chunker(self) -> Chunker:
        return Chunker(setting=self.setting)
    
    def _get_embedding(self) -> EmbeddingService:
        return EmbeddingService(setting=self.setting)
    
    def process(self, inputs: IndexingInput) -> IndexingOutput:
        """Process the input file and return the indexing output.
        
        Args:
            inputs (IndexingInput): Input file path.
        
        Returns:
            IndexingOutput: Indexing output.
        """
        # Convert the file to text
        try:
            document_processor = self._get_convert()
            text = document_processor.process_all()
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            raise e
        
        # Chunk the text
        try:
            chunker = self._get_chunker()
            chunks = chunker.process(ChunkInput(file_path=inputs.file_path))
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise e
        
        # Embed the chunks
        embedding_service = self._get_embedding()
        embeddings = embedding_service.process(EmbeddingInput(chunks=chunks.chunks))
        
        # Return the indexing output
        return IndexingOutput(
            dense_embeddings=embeddings.dense_embeddings,
            sparse_embeddings=embeddings.sparse_embeddings,
        )
import logging
import os
from functools import cached_property
from domain.indexing import EmbeddingService
from domain.indexing import EmbeddingInput
from domain.indexing import Chunker
from domain.indexing import ChunkInput
from domain.indexing import DocumentProcessor

from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings
from infrastructure.qdrant import Qdrant
from infrastructure.qdrant import QdrantInput

logger = logging.getLogger(__name__)

class IndexingInput(BaseModel):
    raw_path: str
    convert_path: str

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
    
    @cached_property
    def _get_embedding(self) -> EmbeddingService:
        return EmbeddingService(settings=self.settings)
    
    @cached_property
    def _get_qdrant(self) -> Qdrant:
        return Qdrant(settings=self.settings)
    
    def process(self, inputs: IndexingInput) -> IndexingOutput:
        """Process the input file and return the indexing output.
        
        Args:
            inputs (IndexingInput): Input file path.
        
        Returns:
            IndexingOutput: Indexing output.
        """
        # Convert the file to text
        try:
            success, output = self._get_convert.process_file(inputs.raw_path)
            if not success:
                logger.error("File conversion failed.")
                raise ValueError("File conversion failed.")
            logger.info("File converted to text successfully.")
            
            os.makedirs(os.path.dirname(inputs.convert_path), exist_ok=True)
            with open(inputs.convert_path, 'w', encoding='utf-8') as f:
                f.write(output)
            logger.info(f"Markdown file saved to {inputs.convert_path}")
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            raise e
        
        # Chunk the text
        try:
            chunks_output = self._get_chunker.process(
                inputs=ChunkInput(
                    convert_path=inputs.convert_path
                )
            )
            if not chunks_output.chunks:
                logger.error("Chunk is empty")
            logger.info("Text chunked successfully.")
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise e
        
        # Embed the chunks
        try:
            embeddings = self._get_embedding.process(
                EmbeddingInput(
                    chunks=chunks_output.chunks,
                    query=""
                )
            )
            logger.info("Chunks embedded successfully.")
        except Exception as e:
            logger.error(f"Error embedding chunks: {e}")
            raise e

        # Store the embeddings in Qdrant
        try:
            self._get_qdrant.insert(
                inputs = QdrantInput(
                    dense_embeddings=embeddings.dense_embeddings,
                    sparse_embeddings=embeddings.sparse_embeddings,
                    payload=embeddings.metadata,
                )
            )
            logger.info("Embeddings stored successfully.")
            return IndexingOutput(status=True)
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            raise e
import logging
from functools import cached_property
from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding
from typing import List, Dict, Any

from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings
from shared.sparse_embedding import SparseEmbeddingData

logger = logging.getLogger(__name__)

class EmbeddingInput(BaseModel):
    chunks: List[Dict[str, Any]]

class EmbeddingOutput(BaseModel):
    dense_embeddings: List[List[float]]
    sparse_embeddings: List[SparseEmbeddingData]
    metadata: List[Dict[str, Any]]

class EmbeddingService(BaseService):
    settings: Settings

    @cached_property
    def load_dense_model(self) -> SentenceTransformer:
        """Load the SentenceTransformer model.

        Returns:
            SentenceTransformer: SentenceTransformer model.
        """
        logger.info(f"Loading SentenceTransformer model from {self.settings.embedding.dense_model_path}")
        return SentenceTransformer(self.settings.embedding.dense_model_path)
    
    @cached_property
    def load_sparse_model(self) -> SparseTextEmbedding:
        """Load the SparseTextEmbedding model.

        Returns:
            SparseTextEmbedding: SparseTextEmbedding model.
        """
        logger.info(f"Loading SparseTextEmbedding model from {self.settings.embedding.sparse_model_path}")
        return SparseTextEmbedding(self.settings.embedding.sparse_model_path)

    def _get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate dense embeddings for a batch of texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of dense embedding vectors
        """
        if not texts:
            return []
    
        valid_texts = [text for text in texts if text and isinstance(text, str)]
        if not valid_texts:
            logger.warning("No valid texts to encode")
            return []
        
        embeddings = []
        for i in range(0, len(valid_texts), self.settings.embedding.max_token_limit):
            batch = valid_texts[i:i + self.settings.embedding.max_token_limit]
            try:
                batch_embeddings = self.load_dense_model.encode(batch).tolist()
                embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error in batch {i//self.settings.embedding.max_token_limit}: {str(e)}")
                embeddings.extend([[0.0] * self.load_dense_model.get_sentence_embedding_dimension()] * len(batch))
        
        return embeddings
    
    def _get_sparse_embedding(self, texts: List[str]) -> List[SparseEmbeddingData]:
        """Generate sparse embeddings for a list of texts.

        Args:
            texts: List of texts to generate sparse embeddings for

        Returns:
            List of sparse embedding data (indices and values)
        """
        if not texts:
            return []
    
        valid_texts = [text for text in texts if text and isinstance(text, str)]
        if not valid_texts:
            logger.warning("No valid texts to encode")
            return []
        
        try:
            sparse_results = list(self.load_sparse_model.embed(valid_texts))
            return [
                SparseEmbeddingData(
                    indices=sparse_result.indices.tolist(),
                    values=sparse_result.values.tolist()
                )
                for sparse_result in sparse_results
            ]
        except Exception as e:
            logger.error(f"Error generating sparse embeddings: {str(e)}")
            return [SparseEmbeddingData(indices=[], values=[]) for _ in valid_texts]

    def process(self, inputs: EmbeddingInput) -> EmbeddingOutput:
        """Process the input chunks and return both dense and sparse embeddings.

        Args:
            inputs (EmbeddingInput): EmbeddingInput object containing chunks

        Returns:
            EmbeddingOutput: EmbeddingOutput object with dense and sparse embeddings
        """
        if not inputs.chunks:
            return EmbeddingOutput(dense_embeddings=[], sparse_embeddings=[])
        
        # Extract texts from chunks
        valid_chunks = [chunk for chunk in inputs.chunks if "content" in chunk and isinstance(chunk["content"], str)]
        if not valid_chunks:
            logger.warning("No valid chunks to encode")
            return EmbeddingOutput(dense_embeddings=[], sparse_embeddings=[])
        
        texts = [chunk["content"] for chunk in valid_chunks]
        
        # Generate embeddings
        dense_embeddings_raw = self._get_embeddings_batch(texts)
        sparse_embeddings = self._get_sparse_embedding(texts)

        metadata = [
            {"content": chunk["content"], "metadata": chunk.get("metadata", {})}
            for chunk in valid_chunks
        ]
        
        return EmbeddingOutput(
            dense_embeddings=dense_embeddings_raw,
            sparse_embeddings=sparse_embeddings,
            metadata=metadata
        )
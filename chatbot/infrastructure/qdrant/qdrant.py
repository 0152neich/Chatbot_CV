from __future__ import annotations
import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import Distance
from qdrant_client.models import Filter, FieldCondition, MatchValue
from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings
from shared.sparse_embedding import SparseEmbeddingData

class QdrantInput(BaseModel):
    dense_embeddings: List[List[float]]
    sparse_embeddings: List[SparseEmbeddingData]
    payload: List[Dict[str, Any]]

class Qdrant(BaseService):
    settings: Settings

    @property
    def client(self) -> QdrantClient:
        return QdrantClient(
            url=self.settings.qdrant.url,
            port=self.settings.qdrant.port
        )

    @property
    def collection(self):
        collection_name = self.settings.qdrant.name
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "dense": models.VectorParams(
                    size=self.settings.qdrant.vector_size,
                    distance=Distance.COSINE
                    )
                },
                sparse_vectors_config={
                    "sparse":models.SparseVectorParams()
                }
            )
        return self.client.get_collection(collection_name)

    def insert(self, inputs: QdrantInput):
        """ Add an embedding to Qdrant

        Args:
            inputs (QdrantInput): A QdrantInput object
        """
        collection=self.collection
        collection_name = self.settings.qdrant.name

        points = [
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector={
                    "dense": inputs.dense_embeddings[i],
                    "sparse": models.SparseVector(
                        indices=inputs.sparse_embeddings[i].indices,
                        values=inputs.sparse_embeddings[i].values
                    )
                },
                payload=inputs.payload[i],
            )
            for i in range(len(inputs.dense_embeddings))
        ]

        self.client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True
        )

    def query(self, dense_query: List[float], sparse_query: List[SparseEmbeddingData], user_name: str, k: int):
        """Search for points in the Qdrant collection based on a query vector and metadata filter.

        Args:
            dense_query (List[float]): The dense query vector to search for.
            sparse_query (List[SparseEmbeddingData]): The sparse query vector to search for.
            metadata (Dict[str, str]): A dictionary containing key-value pairs to filter the points.
            k (int): The maximum number of points to return.

        Returns:
            List[ScoredPoint]: A list of ScoredPoint objects, each containing the point's ID, score,
                payload, and vector (if with_vectors=True). The list length is at most `k`, depending
                on the number of matching points in the collection.
        """
        collection_name = self.settings.qdrant.name
        header_keys = [f"Header_{i}" for i in range(1, 5)]
        filter_conditions = [
            FieldCondition(key=key, match=MatchValue(value=user_name))
            for key in header_keys
        ]
        # query_uint8 = [int(min(max(x * 127.5 + 127.5, 0), 255)) for x in dense_query]
        sparse_dense_rrf_prefetch = models.Prefetch(
            prefetch=[
                models.Prefetch(
                    # prefetch=[
                    #     models.Prefetch(
                    #         query=query_uint8, # integer
                    #         using="dense-uint8",
                    #         limit=40,
                    #     )
                    # ],
                    query=dense_query, # float
                    using="dense",
                    limit=20,
                ),
                models.Prefetch(
                    query=models.SparseVector(
                        indices=sparse_query[0].indices,
                        values=sparse_query[0].values
                    ),
                    using="sparse",
                    limit=20,
                ),
            ],
            query=models.FusionQuery(
                fusion=models.Fusion.RRF,
            ),
        )

        return self.client.query_points(
            collection_name=collection_name,
            query=dense_query,
            prefetch=[sparse_dense_rrf_prefetch],
            using="dense",
            with_payload=True,
            limit=k,
            query_filter=Filter(
                should=filter_conditions,
            )
        )

    def process(self):
        pass
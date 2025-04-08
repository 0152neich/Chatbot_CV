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
    dense_embedding: List[List[float]]
    sparse_embedding: List[SparseEmbeddingData]
    metadata: List[Dict[str, Any]]

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
                    "dense": inputs.dense_embedding[i],
                    "sparse": models.SparseVector(
                        indices=inputs.sparse_embedding[i].indices,
                        values=inputs.sparse_embedding[i].values
                    )
                },
                payload=inputs.metadata[i]
            )
            for i in range(len(inputs.dense_embedding))
        ]

        self.client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True
        )

    def query(self, dense_query: List[float], sparse_query: List[SparseEmbeddingData], metadata: Dict[str, Any], k: int):
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
        key = next(iter(metadata))
        value = metadata[key]
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
                    limit=5,
                ),
                models.Prefetch(
                    query=models.SparseVector(
                        indices=sparse_query[0].indices,
                        values=sparse_query[0].values
                    ),
                    using="sparse",
                    limit=5,
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
                must=[
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                ]
            )
        )

    def process(self):
        pass
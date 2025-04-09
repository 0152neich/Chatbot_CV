import unittest
import numpy as np

from shared.qdrant import QdrantInput
from shared.qdrant import Qdrant
from shared.settings import Settings
from shared.sparse_embedding import SparseEmbeddingData

class TestQdrant(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()
        self.qdrant = Qdrant(settings=self.settings)

    def test_add_embedding(self):
        
        dense_embedding=list(np.random.rand(768).tolist() for _ in range(20))
        sparse_embedding = [
            SparseEmbeddingData(
                indices=(indices := np.random.choice(1000, size=np.random.randint(1, 11), replace=False).tolist()),
                values=np.random.uniform(0, 1, len(indices)).tolist()
            ) for _ in range(20)
        ]
        payload=[{'Header_3': 'DAO DUY CHIEN'} for _ in range(20)]
        self.qdrant.insert(
            inputs = QdrantInput(
                dense_embedding=dense_embedding,
                sparse_embedding=sparse_embedding,
                metadata=payload
            )
        )

    def test_search(self):
        
        dense_query=np.random.rand(768).tolist()
        sparse_query = [
            SparseEmbeddingData(
                indices=(indices := np.random.choice(1000, size=np.random.randint(1, 11), replace=False).tolist()),
                values=np.random.uniform(0, 1, len(indices)).tolist()
            )
        ]
        metadata={'Header_3': 'DAO DUY CHIEN', 'Header_4':'KỸ NĂNG'}
        result = self.qdrant.query(
            dense_query=dense_query,
            sparse_query=sparse_query,
            metadata=metadata,
            k=5
        )
        print(list(point.payload for point in result.points))    

if __name__ == "__main__":
    unittest.main()

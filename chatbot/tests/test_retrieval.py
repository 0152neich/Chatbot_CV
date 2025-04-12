import unittest
import numpy as np
from domain.retrieval import RetrievalInput
from domain.retrieval import RetrievalService
from shared.settings import Settings
from shared.sparse_embedding import SparseEmbeddingData

class TestRetrievalService(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()
        self.retrieval_service = RetrievalService(settings=self.settings)

    def test_process(self):
        dense_query=np.random.rand(768).tolist()
        sparse_query = [
            SparseEmbeddingData(
                indices=(indices := np.random.choice(1000, size=np.random.randint(1, 11), replace=False).tolist()),
                values=np.random.uniform(0, 1, len(indices)).tolist()
            )
        ]
        user_name = "ĐÀO DUY CHIẾN"

        inputs = RetrievalInput(
            dense_query=dense_query,
            sparse_query=sparse_query,
            user_name=user_name
        )

        result = self.retrieval_service.process(inputs=inputs)
        print(result.context)

if __name__ == "__main__":
    unittest.main()
import unittest

from app.indexing import IndexingService
from shared.settings import Settings

class TestIndexing(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()
        self.indexing = IndexingService(settings=self.settings)

    def test_indexing(self):
        
        indexing_output = self.indexing.process()
        self.assertTrue(indexing_output.status)
        self.assertEqual(indexing_output.status, True)

if __name__ == '__main__':
    unittest.main()
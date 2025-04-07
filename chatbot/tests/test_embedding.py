import unittest

from domain.indexing import EmbeddingInput
from domain.indexing import EmbeddingService
from shared.settings import Settings

class TestEmbedding(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()
        self.embedding = EmbeddingService(setting=self.settings)

    def test_embed_chunks(self):
        inputs = EmbeddingInput(chunks=[{'content': 'KỸ SƯ TRÍ TUỆ NHÂN TẠO (AI ENGINEER)  \nEmail: duychien25102004@gmail.com  \nĐiện thoại: 0854013616  \nĐịa chỉ: Thành phố Thanh Hóa, Thanh Hóa  \nGitHub: 0152neich - (https://github.com/0152neich)', 'metadata': {'Header_3': 'ĐÀO DUY CHIẾN'}},
                                        {'content': 'Ngôn ngữ lập trình:  \nC++, Java, Python  \nFrameworks &amp; Thư viện:  \nFastAPI, Streamlit, Scikit-learn, PyTorch, TensorFlow, Keras, spaCy, NLTK, underthesea  \nMachine Learning &amp; Deep Learning:  \nThuật toán ML, CNN, RNN, LSTM, Transformer, GAN  \nXử lý văn bản:', 'metadata': {'Header_3': 'ĐÀO DUY CHIẾN', 'Header_4': 'KỸ NĂNG'}}])
        
        result = self.embedding.process(
            inputs=inputs
        )

        print(result.sparse_embeddings[0])

if __name__ == '__main__':
    unittest.main()
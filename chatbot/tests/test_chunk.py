from domain.indexing import ChunkInput
from domain.indexing import Chunker
from shared.settings import Settings


chunker = Chunker(setting=Settings())

chunk = chunker.process(ChunkInput(file_path='/home/chien/code/Chatbot_RAG/data/convert/DAODUYCHIEN_CV_AI_ENGINEER.md'))

for c in chunk.chunks:
    print(c)
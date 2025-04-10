from domain.indexing import Chunker
from shared.settings import Settings

chunker = Chunker(settings=Settings())
chunk = chunker.process()

for c in chunk.chunks:
    print(c)
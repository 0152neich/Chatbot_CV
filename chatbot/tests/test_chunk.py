from infrastructure.indexing import Chunker
from shared.settings import Settings

chunker = Chunker(setting=Settings())
chunk = chunker.process()

for c in chunk.chunks:
    print(c)
import re
from typing import Any, Dict, List
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings

class ChunkInput(BaseModel):
    file_path: str

class ChunkOutput(BaseModel):
    chunks: List[Dict[str, Any]]

class Chunker(BaseService):
    setting: Settings

    def _get_markdown_headers(self, text: str) -> list[str]:
        """Get the headers from the Markdown text.
        
        Args:
            text (str): Markdown text.
        
        Returns:
            list[str]: List of headers.
        """
        header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header_1"),
                ("##", "Header_2"),
                ("###", "Header_3"),
                ("####", "Header_4"),
                ("#####", "Header_5"),
                ("######", "Header_6"),
            ]
        )
        return header_splitter.split_text(text)
    
    def _get_recusive_splitter(self, text: str) -> list[str]:
        """Split the text recursively.
        
        Args:
            text (str): Text to split.
        
        Returns:
            list[str]: List of text chunks.
        """
        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.setting.chunking.chunk_size,
            chunk_overlap=self.setting.chunking.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            is_separator_regex=False
        )
        return recursive_splitter.split_text(text)
    
    def clean_text(self, text: str) -> str:
        """Clean the text by removing extra spaces, newlines, and specific patterns.
        
        Args:
            text (str): Text to clean.
        
        Returns:
            str: Cleaned text.
        """
        text = re.sub(r'^-| - ·\s*', '', text)
        return text.strip()

    def process(self, inputs: ChunkInput) -> ChunkOutput:
        """Process the Markdown file by splitting based on headers and further chunking.
        
        Args:
            file_path (str): Path to the Markdown file.
        
        Returns:
            list[str]: List of text chunks.
        """
        try:
            with open(inputs.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {inputs.file_path}")
        except Exception as e:
            raise Exception(f"Error reading file {inputs.file_path}: {str(e)}")
        
        content = self.clean_text(content)
        header_docs = self._get_markdown_headers(content)
        
        final_chunks = []
        for doc in header_docs:
            text = doc.page_content
            chunks = self._get_recusive_splitter(text)
            for chunk in chunks:
                if chunk.strip():
                    chunk_dict = {
                        "content": chunk,
                        "metadata": doc.metadata
                    }
                    final_chunks.append(chunk_dict)
        
        return ChunkOutput(chunks=final_chunks)
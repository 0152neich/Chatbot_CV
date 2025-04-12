import re
import os
from typing import Any, Dict, List
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings
from shared.state import StateManager
from shared.clean_text import TextCleaner
from config import STATE_FILE

class ChunkOutput(BaseModel):
    chunks: List[Dict[str, Any]]

class Chunker(BaseService):
    settings: Settings

    @property
    def _get_state_manager(self) -> StateManager:
        return StateManager(
            state_file=STATE_FILE,
        )

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
            chunk_size=self.settings.chunking.chunk_size,
            chunk_overlap=self.settings.chunking.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            is_separator_regex=False
        )
        return recursive_splitter.split_text(text)

    def process(self) -> ChunkOutput:
        """Process the Markdown file by splitting based on headers and further chunking.
        
        Returns:
            list[str]: List of text chunks.
        """
        folder_path = self.settings.chunking.folder_path
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        current_state = self._get_state_manager.get_folder_state(folder_path, file_extension='.md')
        previous_state = self._get_state_manager.load_previous_state()

        files_to_process = self._get_state_manager.get_new_files(current_state, previous_state)
        if not files_to_process and previous_state:
            return ChunkOutput(chunks=[])

        final_chunks = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if not os.path.isfile(file_path) or not filename.lower().endswith('.md'):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            except FileNotFoundError:
                raise FileNotFoundError(f"File not found: {file_path}")
            except Exception as e:
                raise Exception(f"Error reading file {file_path}: {str(e)}")
        
        content = TextCleaner.clean_text(content)
        header_docs = self._get_markdown_headers(content)
        
        for doc in header_docs:
            text = doc.page_content
            chunks = self._get_recusive_splitter(text)
            headers = []
            for i in range(1, 5):
                header_key = f"Header_{i}"
                if header_key in doc.metadata:
                    headers.append(doc.metadata[header_key])
            
            header_str = " > ".join(headers) if headers else ""
            for chunk in chunks:
                if chunk.strip():
                    content_with_header = f"{header_str}: {chunk}" if header_str else chunk
                    chunk_dict = {
                        "content": content_with_header,
                        "metadata": {
                            **doc.metadata,
                        }
                    }
                    final_chunks.append(chunk_dict)
        if final_chunks:
            self._get_state_manager.save_state(current_state)
        
        return ChunkOutput(chunks=final_chunks)
from infrastructure.indexing import convert
from config import DATA_CONVERT, DATA_RAW

file_path = '/home/chien/code/Chatbot_RAG/data/raw/DAODUYCHIEN_CV_AI_ENGINEER.docx'

converter = convert.DocumentProcessor(input_dir=DATA_RAW, output_dir=DATA_CONVERT)
converter.process_file(file_path)
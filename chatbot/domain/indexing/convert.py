import os
import logging
from typing import Optional
from docling.document_converter import DocumentConverter, PdfFormatOption, CsvFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from config import DATA_CONVERT, DATA_RAW
from shared.state import StateManager

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, input_dir: str = DATA_RAW, output_dir: str = DATA_CONVERT) -> None:
        """Initialize the DocumentProcessor with input and output directories."""
        self.input_dir: str = input_dir
        self.output_dir: str = output_dir
        self.state_manager = StateManager(os.path.join(output_dir, "processed_state.json"))
        
        os.makedirs(self.output_dir, exist_ok=True)

    def get_input_format(self, file_path: str) -> Optional[InputFormat]:
        """Determine the InputFormat based on the file extension."""
        ext: str = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return InputFormat.PDF
        elif ext == '.csv':
            return InputFormat.CSV
        elif ext in ['.docx', '.doc']:
            return InputFormat.DOCX
        else:
            return None

    def get_converter(self) -> DocumentConverter:
        """Create a DocumentConverter with format options for all supported formats."""
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.do_cell_matching = False
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

        format_options = {
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
            InputFormat.CSV: CsvFormatOption(),
            InputFormat.DOCX: None
        }
        
        return DocumentConverter(format_options=format_options)

    def process_file(self, file_path: str) -> bool:
        """Process a single file and save the result as Markdown (.md)."""
        filename: str = os.path.basename(file_path)
        input_format: Optional[InputFormat] = self.get_input_format(file_path)
        
        if input_format is None:
            logger.warning(f"Unsupported file format: {filename}")
            return False
        
        converter = self.get_converter()
        
        try:
            res = converter.convert(file_path)
            output = res.document.export_to_markdown(image_placeholder="")
            
            output_filename: str = os.path.splitext(filename)[0] + '.md'
            output_path: str = os.path.join(self.output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            logger.info(f"Converted {filename} to {output_filename}")
            return True
        
        except Exception as e:
            logger.error(f"Error converting {filename}: {str(e)}")
            return False

    def process_all(self) -> None:
        """Process all files (first run) or only new/changed files (subsequent runs)."""
        current_state = self.state_manager.get_folder_state(self.input_dir)
        previous_state = self.state_manager.load_previous_state()

        if not previous_state:
            files_to_process = list(current_state.keys())
            logger.info("First run detected. Processing all files.")
        else:
            files_to_process = self.state_manager.get_new_files(current_state, previous_state)
            logger.info(f"Processing new/changed files: {files_to_process}")

        if not files_to_process:
            logger.info("No new or changed files to process.")
            return

        for filename in files_to_process:
            input_path = os.path.join(self.input_dir, filename)
            if self.process_file(input_path):
                current_state[filename] = os.path.getmtime(input_path)

        self.state_manager.save_state(current_state)
        logger.info("Conversion process completed!")
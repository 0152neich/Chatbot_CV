import os
import logging
from typing import Optional
from docling.document_converter import DocumentConverter, PdfFormatOption, CsvFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

from shared.settings import Settings
logger = logging.getLogger(__name__)

class DocumentProcessor:

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
        pipeline_options.do_table_structure = False
        pipeline_options.table_structure_options.do_cell_matching = False

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
            logger.info(f"Converted {filename} to {output_filename}")
            return True, output
        
        except Exception as e:
            logger.error(f"Error converting {filename}: {str(e)}")
            return False
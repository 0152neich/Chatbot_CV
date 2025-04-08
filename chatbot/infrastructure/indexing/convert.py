import os
import logging
from typing import Optional
from docling.document_converter import DocumentConverter, PdfFormatOption, CsvFormatOption, ImageFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from config import DATA_CONVERT, DATA_RAW

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, input_dir: str = DATA_RAW, output_dir: str = DATA_CONVERT) -> None:
        """Initialize the DocumentProcessor with input and output directories.

        Args:
            input_dir (str): Directory containing the input files. Defaults to DATA_RAW from config.
            output_dir (str): Directory where converted files will be saved. Defaults to DATA_CONVERT from config.
        """
        self.input_dir: str = input_dir
        self.output_dir: str = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

    def get_input_format(self, file_path: str) -> Optional[InputFormat]:
        """Determine the InputFormat based on the file extension.

        Args:
            file_path (str): Path to the file.

        Returns:
            Optional[InputFormat]: The corresponding InputFormat or None if not supported.
        """
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
        """Create a DocumentConverter with format options for all supported formats.

        Returns:
            DocumentConverter: A configured DocumentConverter instance.
        """
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

    def process_file(self, file_path: str) -> None:
        """Process a single file and save the result as Markdown (.md).

        Args:
            file_path (str): Path to the file to be processed.
        """
        filename: str = os.path.basename(file_path)
        input_format: Optional[InputFormat] = self.get_input_format(file_path)
        
        if input_format is None:
            logger.warning(f"Unsupported file format: {filename}")
            return
        
        converter = self.get_converter()
        
        try:
            res = converter.convert(file_path)
            output = res.document.export_to_markdown(image_placeholder="")
            
            output_filename: str = os.path.splitext(filename)[0] + '.md'
            output_path: str = os.path.join(self.output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Converted {filename} to {output_filename}")
            logger.info(f"Converted {filename} to {output_filename}")
        
        except Exception as e:
            logger.error(f"Error converting {filename}: {str(e)}")
            return

    def process_all(self) -> None:
        """Process all files in the input directory."""
        for filename in os.listdir(self.input_dir):
            input_path: str = os.path.join(self.input_dir, filename)
            
            # Skip if not a file
            if not os.path.isfile(input_path):
                continue
            
            self.process_file(input_path)
        
        print("Conversion process completed!")
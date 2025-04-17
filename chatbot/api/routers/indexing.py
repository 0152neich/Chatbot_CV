from __future__ import annotations

import logging
import os
from fastapi import APIRouter
from fastapi import status
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import File
from api.helpers.exception_handler import ResponseMessage
from shared.settings import Settings
from app.indexing import IndexingService
from app.indexing import IndexingInput

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
settings = Settings()

indexing = APIRouter(prefix="/v1")

try:
    logger.info("Init indexing router")
    indexing_service = IndexingService(settings=Settings())
    logger.info("Indexing service initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing indexing service: {e}")
    raise e

@indexing.post(
    '/indexing',
    responses={
        status.HTTP_200_OK: {
            'content': {
                'application/json': {
                    'example': {
                        'message': ResponseMessage.SUCCESS,
                        'info': {
                            'status': True,
                        },
                    },
                },
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            'description': 'Bad Request',
            'content': {
                'application/json': {
                    'example': {
                        'message': ResponseMessage.BAD_REQUEST,
                    },
                },
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'description': 'Internal Server Error',
            'content': {
                'application/json': {
                    'example': {
                        'message': ResponseMessage.INTERNAL_SERVER_ERROR,
                    },
                },
            },
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            'description': 'Unprocessable Entity - Format is not supported',
            'content': {
                'application/json': {
                    'example': {
                        'message': ResponseMessage.UNPROCESSABLE_ENTITY,
                    },
                },
            },
        },
        status.HTTP_404_NOT_FOUND: {
            'description': 'Destination Not Found',
            'content': {
                'application/json': {
                    'example': {
                        'message': ResponseMessage.NOT_FOUND,
                    },
                },
            },
        },
    },
)

async def indexing_file(inputs: UploadFile = File(...)):

    # Check if the file is None
    if inputs is None:
        logger.error("File is None")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseMessage.BAD_REQUEST,
        )
    
    # Check type of file
    allowed_extensions = {'.pdf', '.docx', '.csv'}
    file_ext = os.path.splitext(inputs.filename)[1].lower()
    if file_ext not in allowed_extensions:
        logger.error(f"Unsupported file format: {file_ext}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ResponseMessage.UNPROCESSABLE_ENTITY,
        )
    
    raw_path = os.path.join(settings.indexing.raw_path, inputs.filename)
    convert_path = os.path.join(settings.indexing.convert_path, os.path.splitext(inputs.filename)[0] + '.md')
    os.makedirs(settings.indexing.raw_path, exist_ok=True)
    
    # Check if the directory exists
    try:
        # save to DATA_RAW
        with open(raw_path, 'wb') as f:
            content = await inputs.read()
            f.write(content)
        await inputs.close()
        logger.info(f"File saved successfully to {raw_path}")
    except Exception as e:
        logger.error(f"Error writing file to {raw_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseMessage.INTERNAL_SERVER_ERROR,
        )

    try:
        logger.info("Starting indexing process...")
        indexing_output = indexing_service.process(
            inputs=IndexingInput(
                raw_path=raw_path,
                convert_path=convert_path
            )
        )
        return {
            "message": ResponseMessage.SUCCESS,
            "info": {
                "status": indexing_output.status
            }
        }
    except FileExistsError as e:
        logger.error(f"File already exists: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseMessage.BAD_REQUEST,
        )
    except FileNotFoundError as e:
        logger.error(f"File or folder not found during indexing: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseMessage.NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"Error during indexing process: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseMessage.INTERNAL_SERVER_ERROR,
        )
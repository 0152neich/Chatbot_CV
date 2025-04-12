from __future__ import annotations
import logging
from fastapi import APIRouter
from fastapi import status
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from api.models.chabot import APIInput
from api.models.chabot import APIOutput
from app.query import ChatbotService
from app.query import ChatbotInput
from api.helpers.exception_handler import ResponseMessage
from shared.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

chatbot = APIRouter(prefix="/v1")

@chatbot.post(
    '/chatbot',
    response_model=APIOutput,
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

async def chatbot_service(inputs: APIInput) -> APIOutput:

    if inputs.query is None:
        logger.error("Query is None")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseMessage.BAD_REQUEST,
        )
    
    try:
        chatbot_service = ChatbotService(settings=Settings())
        logger.info("Init chatbot service success!")
    except Exception as e:
        logger.error(f"Error to init chatbot service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseMessage.INTERNAL_SERVER_ERROR,
        )
    
    try:
        response = chatbot_service.process(
            ChatbotInput(
                query=inputs.query,
                user_name=inputs.user_name
            )
        )
        logger.info("Chatbot processed query successfully")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'message': ResponseMessage.SUCCESS,
                'info': {
                    'status': True,
                    'response': response.response
                }
            }
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseMessage.INTERNAL_SERVER_ERROR,
        )
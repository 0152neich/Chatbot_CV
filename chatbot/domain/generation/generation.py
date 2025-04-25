import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from typing import List, Dict, Any
from shared.base import BaseModel
from shared.base import BaseService
from shared.clean_text import TextCleaner
from shared.settings import Settings

logger = logging.getLogger(__name__)
class GenerationInput(BaseModel):
    query: str
    chat_history: List[BaseMessage]
    retrieved_info: List[Dict[str, Any]]

class GenerationOutput(BaseModel):
    response: str

class GenerationService(BaseService):
    settings: Settings

    def process(self, inputs: GenerationInput) -> GenerationOutput:
        """Generate a response based on the input query and chat history.

        Args:
            inputs (GenerationInput): Input data containing the query and chat history.

        Returns:
            GenerationOutput: Output data containing the generated response.
        """
        try:
            llm = ChatOpenAI(
                model=self.settings.generation.model,
                temperature=self.settings.generation.temperature,
                max_tokens=self.settings.generation.max_tokens,
                streaming=True,
                api_key=self.settings.generation.api_key,
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise e
        
        retrieved_info_str = " ".join(
            [
                f"Content: {doc.get('content', 'N/A')}"
                for doc in inputs.retrieved_info
            ]
        )
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system",
                "Bạn là ChatbotAI, trợ lý thân thiện chuyên trả lời câu hỏi về CV. "
                "Dựa trên thông tin CV, trả lời bằng tiếng Việt, tự nhiên, dễ hiểu, chỉ dùng thông tin từ CV, bỏ ký hiệu thừa. "
                "Dùng liên từ để câu văn mượt mà, ưu tiên thông tin liên quan. "
                "Nếu không có thông tin, trả lời: 'Tôi không tìm thấy thông tin trong CV.' "
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{retrieved_info}\nCâu hỏi: {input}")
            ])

            chain = prompt | llm
            response = chain.invoke({
                "input": inputs.query,
                "chat_history": inputs.chat_history,
                "retrieved_info": retrieved_info_str
            })
            cleaned_response = TextCleaner().clean_text(response.content)
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            raise e

        return GenerationOutput(response=response.content)

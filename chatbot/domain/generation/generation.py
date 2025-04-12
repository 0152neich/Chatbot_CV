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
            prompt = ChatPromptTemplate.from_messages([
            ("system",
                "Bạn là ChatbotAI chuyên dụng trả lời câu hỏi về CV dựa trên thông tin trong tài liệu."
                "Trả lời chính xác và đầy đủ thông tin một cách tự nhiên."
                "Nếu không có thông tin hoặc thông tin không liên quan, nói 'Không có thông tin trong CV.'"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{retrieved_info}\nCâu hỏi: {input}")
            ])
            retrieved_info_str = " ".join(
                [
                    f"Content: {doc.get('content', 'N/A')}"
                    for doc in inputs.retrieved_info
                ]
            )
            logger.info("Retrieved Info:", retrieved_info_str)
            chain = prompt | llm
            response = chain.invoke({
                "input": inputs.query,
                "chat_history": inputs.chat_history,
                "retrieved_info": retrieved_info_str
            })
            response = TextCleaner().clean_text(response.content)
            return GenerationOutput(response=response)
        except Exception as e:
            return GenerationOutput(response=f"Error: {str(e)}")
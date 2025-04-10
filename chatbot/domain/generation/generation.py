from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from typing import List, Dict, Any
from shared.base import BaseModel
from shared.base import BaseService
from shared.settings import Settings

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
                "Trả lời câu hỏi về CV chỉ dựa trên thông tin trong tài liệu. "
                "Trả lời ngắn gọn, chính xác. Nếu không có thông tin hoặc thông tin không liên qian, nói 'Không có thông tin trong CV.'"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{retrieved_info}\nCâu hỏi: {input}")
            ])
            retrieved_info_str = "\n".join(
                [f"Content: {doc.get('content', 'N/A')}\nMetadata: {doc.get('metadata', 'N/A')}" 
                for doc in inputs.retrieved_info]
            )

            chain = prompt | llm
            response = chain.invoke({
                "input": inputs.query,
                "chat_history": inputs.chat_history,
                "retrieved_info": retrieved_info_str
            })
            return GenerationOutput(response=response.content)
        except Exception as e:
            return GenerationOutput(response=f"Error: {str(e)}")
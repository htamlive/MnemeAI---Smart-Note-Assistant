from langsmith import traceable
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, ChatMessage
from langchain_core.runnables import chain
import datetime

import config.config as config
import llm.prompt_template as prompt_template
from .tool_executor import ToolExecutor

from .models import UserData


class LLM:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = ChatOpenAI(model=model, api_key=config.OPENAI_API_KEY)
        self.model = self.model.bind(stop=["Observation:"])
        self.tool_executor = ToolExecutor()
        self.tools_interface = self.load_tools_interface()
        self.prompt_template_1 = ChatPromptTemplate.from_messages(prompt_template.prompt_template_1)
        self.prompt_template_2 = ChatPromptTemplate.from_messages(prompt_template.prompt_template_2)
    
    def get_current_datetime(self) -> str:
        current_datetime = datetime.datetime.now()

        return f"{current_datetime.strftime('%Y-%m-%d %H:%M:%S %A')}"

    def load_tools_interface(self) -> str:
        with open("llm/tools_interface.py", "r") as f:
            return f.read()


    
    async def execute_llm(self, user_data: UserData, user_request: str) -> str | None:
        def final_message_parser(ai_message: AIMessage) -> str:
            return ai_message.content
        
        @chain
        async def custom_chain(user_request: str) -> str | None:
            try:
                chain_1 = self.prompt_template_1 | self.model
                response_1: AIMessage = chain_1.invoke({"tools": self.tools_interface, "request": user_request, "datetime": self.get_current_datetime()})
                tool_response = await self.tool_executor.execute_from_string(user_data, response_1.content)

                chain_2 = self.prompt_template_2 | self.model | final_message_parser
                response_2: str = chain_2.invoke({"ai_message": response_1.content, "result": tool_response, "tools": self.tools_interface, "request": user_request, "datetime": self.get_current_datetime()})

                return response_2
            except Exception as e:
                return f"Error: {str(e)}"
        return await custom_chain.ainvoke(user_request)
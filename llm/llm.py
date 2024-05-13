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

from ._tools_manager import ToolType, ToolManager


class LLM:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = ChatOpenAI(model=model, api_key=config.OPENAI_API_KEY)
        self.model = self.model.bind(stop=["Observation:"])
        self.tool_executor = ToolExecutor()
        self.prompt_template_1 = ChatPromptTemplate.from_messages(prompt_template.prompt_template_1)
        self.prompt_template_2 = ChatPromptTemplate.from_messages(prompt_template.prompt_template_2)

        self.tool_manager = ToolManager()
    
    def get_current_datetime(self) -> str:
        current_datetime = datetime.datetime.now()

        return f"{current_datetime.strftime('%Y-%m-%d %H:%M:%S %A')}"

    
    async def execute_prompting(self, user_data: UserData, user_request: str) -> str | None:
        function_map, tool_interfaces = self.tool_manager.get_tools([tool_type for tool_type in ToolType])
        return await self._llm_invoke(user_data, user_request, function_map, tool_interfaces)

    async def add_note(self, user_data: UserData, note_text: str) -> str | None:
        function_map, tool_interfaces = self.tool_manager.get_tools([ToolType.ADD_NOTE])
        return await self._llm_invoke(user_data, note_text, function_map, tool_interfaces)
    
    async def add_task(self, user_data: UserData, task_text: str) -> str | None:
        function_map, tool_interfaces = self.tool_manager.get_tools([ToolType.CREATE_TASK])
        # print("Function map:", function_map)
        # print("Tool interfaces:", tool_interfaces)
        return await self._llm_invoke(user_data, task_text, function_map, tool_interfaces)

    async def _llm_invoke(self, user_data: UserData, user_request: str, function_map: dict[str, callable], tool_interfaces: str) -> str:
        def final_message_parser(ai_message: AIMessage) -> str:
            return ai_message.content
        
        @chain
        async def custom_chain(user_request: str) -> str | None:
            try:
                chain_1 = self.prompt_template_1 | self.model

                response_1: AIMessage = chain_1.invoke({"tools": tool_interfaces, "request": user_request, "datetime": self.get_current_datetime()})
                
                tool_response = await self.tool_executor.execute_from_string(user_data, response_1.content, function_map)

                chain_2 = self.prompt_template_2 | self.model | final_message_parser
                response_2: str = chain_2.invoke({"ai_message": response_1.content, "result": tool_response, "tools": tool_interfaces, "request": user_request, "datetime": self.get_current_datetime()})

                return response_2
            except Exception as e:
                return f"Error: {str(e)}"
        return await custom_chain.ainvoke(user_request)
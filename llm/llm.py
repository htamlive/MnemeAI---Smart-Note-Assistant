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
        self.prompt_template_1 = ChatPromptTemplate.from_messages(prompt_template.prompt_template_rules)
        self.prompt_template_2 = ChatPromptTemplate.from_messages(prompt_template.prompt_template_action)

        self.tool_manager = ToolManager()
    
    def get_current_datetime(self, timezone: str) -> str:

        current_datetime = datetime.datetime.now(timezone)

        print(f'Timezone from get_current_datetime: {timezone}')

        print(current_datetime)

        return f"{current_datetime.strftime('%Y-%m-%d %H:%M:%S %A')}"

    
    async def execute_prompting(self, user_data: UserData, user_request: str) -> str | None:
        function_map, tool_interfaces = self.tool_manager.get_tools([tool_type for tool_type in ToolType])
        print(len(function_map))
        return await self._llm_invoke(user_data, user_request, function_map, tool_interfaces)

    async def add_note(self, user_data: UserData, note_text: str) -> str | None:
        function_map, tool_interfaces = self.tool_manager.get_tools([ToolType.CREATE_NOTES])
        return await self._llm_invoke(user_data, note_text, function_map, tool_interfaces)
    
    async def add_task(self, user_data: UserData, task_text: str) -> str | None:
        function_map, tool_interfaces = self.tool_manager.get_tools([ToolType.CREATE_TASK])
        # print("Function map:", function_map)
        # print("Tool interfaces:", tool_interfaces)
        return await self._llm_invoke(user_data, task_text, function_map, tool_interfaces)
    
    async def save_task_time(self, user_data: UserData, time_text: str) -> str | None:
        function_map, tool_interfaces = self.tool_manager.get_tools([ToolType.SAVE_TASK_TIME])
        return await self._llm_invoke(user_data, time_text, function_map, tool_interfaces)
    
    async def update_timezone(self, user_data: UserData, timezone_text: str) -> str | None:
        function_map, tool_interfaces = self.tool_manager.get_tools([ToolType.UPDATE_TIMEZONE_UTC])
        return await self._llm_invoke(user_data, timezone_text, function_map, tool_interfaces, update_timezone=True)
    
    async def retrieve_knowledge_from_notes(self, user_data: UserData, prompt: str) -> str | None:
        function_map, tool_interfaces = self.tool_manager.get_tools([ToolType.RETRIEVE_KNOWLEDGE_FROM_NOTES])
        return await self._llm_invoke(user_data, prompt, function_map, tool_interfaces)

    async def _llm_invoke(self, user_data: UserData, user_request: str, function_map: dict[str, callable], tool_interfaces: str, update_timezone=False) -> str | None:        
        
        
        timezone = user_data.timezone

        
        if(not timezone and not update_timezone):
            return "Error: Timezone not set. Please set your timezone first using /timezone command. The time zone will be stored in each user's session."
        
        if(not timezone):
            tmp_user_data = UserData()
            await self.tool_manager.function_map[ToolType.UPDATE_TIMEZONE_UTC](tmp_user_data, 0)

            timezone = tmp_user_data.timezone

        def final_message_parser(ai_message: AIMessage) -> str:
            return ai_message.content
        
        current_time = self.get_current_datetime(timezone)

        print(f'Timezone from _llm_invoke: {timezone}, current_time: {current_time}')
        
        @chain
        async def custom_chain(user_request: str) -> str | None:
            try:
                chain_1 = self.prompt_template_1 | self.model

                response_1: AIMessage = chain_1.invoke({"tools": tool_interfaces, "request": user_request, "datetime": current_time})
                
                tool_response = await self.tool_executor.execute_from_string(user_data, response_1.content, function_map)

                chain_2 = self.prompt_template_2 | self.model | final_message_parser
                response_2: str = chain_2.invoke({"ai_message": response_1.content, "result": tool_response, "tools": tool_interfaces, "request": user_request, "datetime": self.get_current_datetime(timezone)})

                return response_2
            except Exception as e:
                return f"Error: {str(e)}"
        res =  await custom_chain.ainvoke(user_request)
        return res
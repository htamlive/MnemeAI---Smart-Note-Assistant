from typing import Tuple
from ._tools import *

import enum

class ToolType(enum.Enum):
    CREATE_TASK = "create_task"
    DELETE_TASK = "delete_task"
    SAVE_TASK_TITLE = "save_task_title"
    SAVE_TASK_DETAIL = "save_task_detail"
    SAVE_TASK_TIME = "save_task_time"
    SHOW_TASK_DETAIL = "show_task_detail"
    SHOW_TASK_LIST = "show_task_list"

    CREATE_NOTES = "create_notes"
    DELETE_NOTES = "delete_notes"
    SAVE_NOTES_TITLE = "save_notes_title"
    SAVE_NOTES_DETAIL = "save_notes_detail"
    SHOW_NOTES_LIST = "show_notes_list"
    SHOW_NOTES_DETAIL = "show_notes_detail"

    UPDATE_TIMEZONE_UTC = "update_timezone_utc"
    RETRIEVE_KNOWLEDGE_FROM_NOTES = "retrieve_knowledge_from_notes"

class ToolManager():
    def __init__(self):
        self.function_map: dict[ToolType, callable] = {
            ToolType.CREATE_TASK: create_task,
            ToolType.DELETE_TASK: delete_task,
            ToolType.SAVE_TASK_TITLE: save_task_title,
            ToolType.SAVE_TASK_DETAIL: save_task_detail,
            ToolType.SAVE_TASK_TIME: save_task_time,
            ToolType.SHOW_TASK_DETAIL: show_task_detail,
            ToolType.SHOW_TASK_LIST: show_task_list,

            ToolType.CREATE_NOTES: create_notes,
            ToolType.DELETE_NOTES: delete_notes,
            ToolType.SAVE_NOTES_TITLE: save_notes_title,
            ToolType.SAVE_NOTES_DETAIL: save_notes_detail,
            ToolType.SHOW_NOTES_LIST: show_notes_list,
            ToolType.SHOW_NOTES_DETAIL: show_notes_detail,

            ToolType.UPDATE_TIMEZONE_UTC: update_timezone_utc,
            ToolType.RETRIEVE_KNOWLEDGE_FROM_NOTES: retrieve_knowledge_from_notes
        }


        self.tool_type_lookup: dict[str, ToolType] = {
            tool_type.value: tool_type for tool_type in ToolType
        }

        self._load_tools_interface()
            

    def _load_tools_interface(self):

        self.function_interfaces = {}

        sections = open("llm/tools_interface.py", "r").read().strip().split('#')
        for section in sections:
            # find the first "def" in the section
            start = section.find("def")
            if start == -1:
                continue
            
            if(not (start == 0 or section[start-1] == '\n')):
                raise Exception("Invalid tool definition")
            
            function_interface = section[start:].strip()

            # get the function name
            end = function_interface.find("(")
            if end == -1:
                raise Exception("Invalid tool definition")
            
            function_name = function_interface[start + 3:end].strip()

            
            tool_type = self.tool_type_lookup.get(function_name)

            if tool_type is None:
                raise Exception(f"Invalid tool definition: '{function_name}' not found in ToolType enum")
            
            self.function_interfaces[tool_type] = function_interface
            

    def get_tools(self, tool_types: List[ToolType]) -> Tuple[dict[str, callable], str]:
        tools = {}
        function_interfaces = []
        for tool_type in tool_types:
            if tool_type in self.function_map:
                tools[tool_type.value] = self.function_map[tool_type]
                function_interfaces.append(self.function_interfaces[tool_type])
            else:
                raise Exception(f"Error: Function '{tool_type.value}' not found.")
            
        interfaces = "\n".join(function_interfaces)

        return tools, interfaces
    
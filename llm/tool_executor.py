import re
import ast
from typing import List

# Define mock functions
def create_task(title: str, body: str, datetime) -> str:
    return f"Created task: {title}, Body: {body}, Due: {datetime}"

def delete_task(task_name: str) -> str:
    return f"Deleted task: {task_name}"

def add_note(title: str, content: str) -> str:
    return f"Added note: {title}, Note: {content}"

def get_note(queries_str: str) -> List[str]:
    return ['Building a rocket', 'fighting a mummy', 'climbing up the Eiffel Tower']

def return_item_idx(index: int) -> int:
    return index

def get_all_details_for_note(title: str, body: str) -> list[str]:
    return [title, body]

def get_all_details_for_task(title: str, body: str, datetime: str) -> list[str]:
    return [title, body, datetime]

# @traceable
class ToolExecutor:
    def __init__(self):
        self.function_map = {
            'create_task': create_task,
            'delete_task': delete_task,
            'add_note': add_note,
            'get_note': get_note,
            'return_item_idx': return_item_idx,
            'get_all_details_for_note': get_all_details_for_note,
            'get_all_details_for_task': get_all_details_for_task
        }

    def execute_from_string(self, chat_id, raw_str) -> str:
        # Extract function call string using regular expression
        function_call_match = re.search(r'(\w+)\((.*?)\)', raw_str)
        
        if function_call_match:
            # Extract function name and its arguments
            function_name = function_call_match.group(1)
            arguments_str = function_call_match.group(2)

            # Parse arguments string into a Python literal
            try:
                arguments = ast.literal_eval(arguments_str)

                # If the argument is a single value, convert it to a tuple
                if not isinstance(arguments, tuple):
                    arguments = (arguments,)
            except (SyntaxError, ValueError):
                return "Error: Failed to parse arguments string."
            
            # Check if function exists
            if function_name in self.function_map:
                # Execute the function call
                return self.function_map[function_name](*arguments)
            else:
                return f"Error: Function '{function_name}' not found."
        else:
            return "No function call found in the raw string."


if __name__ == "__main__":
    task_executor = ToolExecutor()
    raw_str = """Thought: I need to create a task for the homework due tomorrow.
Action: get_note("xz")"""

    print(task_executor.execute_from_string(raw_str))

from datetime import timezone, datetime, timedelta
import re
import ast


# @traceable
class ToolExecutor:
        
    async def execute_from_string(self, user_data, raw_str, function_map: dict[str, callable]) -> str:
        # Extract function call string using regular expression
        function_call_match = re.search(r"(\w+)\((.*?)\)", raw_str)

        if function_call_match:
            # Extract function name and its arguments
            function_name = function_call_match.group(1)
            arguments_str = function_call_match.group(2)

            if arguments_str == "":
                arguments_str = "()"

            # Parse arguments string into a Python literal
            try:
                arguments = ast.literal_eval(arguments_str)

                # If the argument is a single value, convert it to a tuple
                if not isinstance(arguments, tuple):
                    arguments = (arguments,)

                arguments = (user_data, *arguments)
            except (SyntaxError, ValueError):
                return "Error: Failed to parse arguments string."

            # Check if function exists
            if function_name in function_map:
                # Execute the function call
                return await function_map[function_name](*arguments)
            else:
                return f"Error: Function '{function_name}' not found."
        else:
            return "No function call found in the raw string."


if __name__ == "__main__":
    task_executor = ToolExecutor()
    raw_str = """Thought: I need to create a task for the homework due tomorrow.
Action: get_note("xz")"""

    print(task_executor.execute_from_string(raw_str))

import re


file_path = input("Enter the file path: ")

data = open(file_path, 'r').read()

lines = data.split("\n")

for line in lines:
    if("def" in line and 'self' in line):
        is_async = "async" in line
        method_name = re.search(r"def\s+(\w+)\(", line).group(1)

        method_parameters = re.search(r"\((.*?)\)", line).group(1)

        method_parameters = method_parameters.split(", ")
    

        if(not (method_return_type:= re.search(r"->\s+(\w+)", line))):
            method_return_type = "None"

        else:
            method_return_type = method_return_type.group(1)

        if(method_parameters and method_parameters[0] == "self"):
            method_parameters.pop(0)

        formatted_parameters = ", ".join(method_parameters)

        formatted_method = "async " if is_async else ""

        formatted_method += f"{method_name}({formatted_parameters}): {method_return_type}"

        print(formatted_method)
        



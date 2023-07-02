import docstring_parser
import inspect
import functools
from typing import Callable

openai_functions = []

def extract_function_info(func: Callable) -> dict:
    # Parse the docstring
    parsed_docstring = docstring_parser.parse(func.__doc__)

    # Get information about function parameters
    params = inspect.signature(func).parameters

    properties = {}
    required_params = []
    for k, v in params.items():
        if k == "self":
            continue  # Skip 'self' parameter for instance methods

        param_type = v.annotation.__name__ if v.annotation != inspect.Parameter.empty else "string"
        param_description = ""
        default_value = v.default if v.default != inspect.Parameter.empty else None

        # Find the corresponding parameter in the parsed docstring
        for param_doc in parsed_docstring.params:
            if param_doc.arg_name == k:
                param_description = param_doc.description
                break

        properties[k] = {
            "type": param_type,
            "description": param_description,
        }

        if default_value is not None:
            properties[k]["default"] = default_value
        else:
            required_params.append(k)

    spec = {
        "name": func.__name__,
        "description": parsed_docstring.short_description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required_params,
        },
    }

    return spec

def openaifunc(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    spec = extract_function_info(func)
    openai_functions.append(spec)
    # Print the list of decorated functions
    for func in openai_functions:
        print(func)

    return wrapper

async def get_openai_funcs():
    return openai_functions
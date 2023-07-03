import docstring_parser
import inspect
import functools
from typing import Callable

openai_functions = []

def extract_function_info(func: Callable) -> dict:
    parsed_docstring = docstring_parser.parse(func.__doc__)
    params = inspect.signature(func).parameters

    type_mapping = {
        "int": "integer",
        "float": "number",
        "str": "string",
        "bool": "boolean",
        "list": "array",
        "tuple": "array",
        "dict": "object",
        "None": "null",
    }

    properties = {}
    required_params = []
    for k, v in params.items():
        if k == "self":
            continue

        param_type = type_mapping.get(v.annotation.__name__, "string") if v.annotation != inspect.Parameter.empty else "string"
        param_description = ""

        default_value_exists = v.default != inspect.Parameter.empty

        for param_doc in parsed_docstring.params:
            if param_doc.arg_name == k:
                param_description = param_doc.description
                break

        properties[k] = {
            "type": param_type,
            "description": param_description,
        }

        if not default_value_exists:
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
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    spec = extract_function_info(func)
    openai_functions.append(spec)

    return wrapper

async def get_openai_funcs():
    return openai_functions
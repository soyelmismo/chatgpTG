import os
import importlib
import glob

import docstring_parser
import inspect
import functools
from typing import Callable

openai_functions = []

def import_functions_from_directory(directory, module_prefix):
    function_map = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_path = os.path.join(root, file).replace("\\", "/")
                relative_module_path = os.path.relpath(module_path, directory).replace(".py", "")
                import_path = f"{module_prefix}.{relative_module_path.replace('/', '.')}"
                module = importlib.import_module(import_path)

                for function_name, function_obj in inspect.getmembers(module, inspect.isfunction):
                    function_map[function_name] = function_obj

    return function_map

def _get_metadata(function_map):
    metadata = []
    for function_name, function_obj in function_map.items():
        if hasattr(function_obj, "_openai_metadata"):
            metadata.append(function_obj._openai_metadata)
    return metadata

def get_openai_funcs(return_function_objects = None):
    function_map = import_functions_from_directory("bot/functions/openai_front", "bot.functions.openai_front")

    if return_function_objects:
        return function_map
    else:
        return _get_metadata(function_map)

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
    wrapper._openai_metadata = spec

    return wrapper

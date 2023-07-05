import openai
import json
from datetime import datetime
from bot.src.utils.config import api, proxy_raw, usar_funciones

if usar_funciones:
    from .openai_functions_extraction import get_openai_funcs
    imported_functions = get_openai_funcs(return_function_objects = True)
    functions_data = get_openai_funcs()

async def process_function_argument(response):
    arguments_list = []
    async for response_item in response:
        try:
            arguments_value = response_item.choices[0].delta.function_call.get("arguments", "")
            if arguments_value is not None: arguments_list.append(arguments_value)
            if response_item.choices[0].delta.get("finish_reason") == "function_call": break
        except Exception: continue
    # Now that we have the list of argument fragments, join them into a single string
    if not arguments_list: return None
    # Now that we have the complete JSON string, we can parse it
    arguments = json.loads("".join(arguments_list))
    return arguments

async def handle_response_item(self, old_response, fn, kwargs):

    function_name, arguments = None, None

    if self.diccionario.get("stream") == False:
        status, result, function_name, arguments = process_non_stream_response(self, old_response)
        if result != None:
            yield status, result
    else:
        async for status, result, function_name, arguments in process_stream_response(self, old_response):
            if function_name and arguments:
                break
            yield status, result

    if arguments:
        async for status, result in process_arguments_and_generate_response(self, function_name, fn, arguments, kwargs):
            yield status, result

def process_non_stream_response(self, response):
    if hasattr(response.choices[0], "message") and "function_call" in response.choices[0].message:
        function_name = response.choices[0].message.function_call.get("name")
        arguments = json.loads(response.choices[0].message.function_call.get("arguments"))
        return None, None, function_name, arguments
    else:
        return None, eval(self.iter), None, None

async def process_stream_response(self, old_response):
    function_name, arguments = None, None
    async for response_item in old_response:
        if hasattr(response_item.choices[0], "delta") and "function_call" in response_item.choices[0].delta:
            function_name = response_item.choices[0].delta.function_call.get("name")
            arguments = await process_function_argument(old_response)
        else:
            self.answer += eval(self.iter)
            yield "not_finished", self.answer, None, None
    if arguments != None:
        yield None, None, function_name, arguments

async def process_arguments_and_generate_response(self, function_name, fn, arguments, kwargs):
    self = await procesar_nuevos_datos(self, function_name, arguments, kwargs)
    response = await fn(**self.diccionario)

    if self.diccionario.get("stream") == False:
        yield None, eval(self.iter)
    else:
        async for response_item in response:
            if response_item.choices[0].delta.get("finish_reason") == "stop":
                yield "finished", self.answer
                break
            self.answer += eval(self.iter)
            yield "not_finished", self.answer

async def procesar_nuevos_datos(self, function_name, arguments, kwargs):
    function_response = await imported_functions[function_name](self, **arguments)
    new_dialog_message = {'function': f'{function_name}', "func_cont": f'{function_response}', "date": datetime.now()}
    from bot.src.utils.misc import update_dialog_messages
    from bot.src.utils.preprocess import count_tokens, make_messages
    await update_dialog_messages(self.chat, new_dialog_message)
    data, completion_tokens, chat_mode = await count_tokens.putos_tokens(self.chat, kwargs["_message"])

    self.diccionario["max_tokens"] = completion_tokens

    messages = await make_messages.handle(self, kwargs["_message"], data, chat_mode)

    self.diccionario["messages"] = messages
    self.diccionario.pop("functions")
    self.diccionario.pop("function_call")
    return self

async def _openai(self, **kwargs):
    try:
        if self.proxies is not None:
            openai.proxy = {f'{proxy_raw.split("://")[0]}': f'{proxy_raw}'}

        api_info = api["info"].get(self.api, {})
        openai.api_key = str(api_info.get("key", ""))
        openai.api_base = str(api["info"][self.api].get("url"))
        self, fn = await last_config(self, kwargs)
        response = await fn(**self.diccionario)
        async for response_status, answer in handle_response_item(self, response, fn, kwargs):
            yield response_status, answer
    except Exception as e:
        raise ConnectionError(f'_get_openai_answer: {e}')

async def last_config(self, kwargs):
    if self.diccionario.get("stream") == False:
        if kwargs["messages"] != None:
            self.iter = 'response.choices[0].message["content"]'
        else:
            self.iter = 'response.choices[0].text'
    else:
        if kwargs["messages"] != None:
            self.iter = 'response_item.choices[0].delta.get("content", "")'
        else:
            self.iter = 'response_item.choices[0].text'

    if kwargs["messages"] != None:
        self.diccionario.update({"messages": kwargs["messages"], "model": self.model})
        if usar_funciones:
            self.diccionario["functions"] = functions_data
            self.diccionario["function_call"] = "auto"
        fn = openai.ChatCompletion.acreate
    else:
        self.diccionario.update({"prompt": kwargs["prompt"], "model": self.model})
        fn = openai.Completion.acreate

    return self, fn
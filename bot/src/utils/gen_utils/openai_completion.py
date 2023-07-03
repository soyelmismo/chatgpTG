import openai
import json
from asyncio import sleep
from datetime import datetime
from bot.src.apis import duckduckgo, smart_gsm
#from bot.src.utils.gen_utils.openai_decorator.openai_decorator import openaifunc, get_openai_funcs
from .openai_functions_extraction import openaifunc, get_openai_funcs
from bot.src.utils.config import api, proxy_raw, usar_funciones

@openaifunc
async def search_on_internet(self, query: str, search_type: str, timelimit: str = None) -> str:
    """
    Search information and news on internet
    Reveives a search query to search information on the web returning it to talk freely to the user about the results giving pleasant answers.

    Args:
        query (str): the text that will be searched on the internet
        search_type (str): use "text" or "news" depending of what the user has requested
        timelimit (str): use "d" if latest news from today, for other time limits: "w", "m", "y". Defaults to None. they are d(day), w(week), m(month), y(year).
    
    Returns:
        str: the search / news results to inform the user
    """
    if query:
        return await duckduckgo.search(self, query = query, gptcall = True, timelimit = timelimit, type = search_type)
    else: return "No se encontraron argumentos de busqueda. por favor pidele al usuario qué quiere buscar."

@openaifunc
async def search_smartphone_info(self, model: str) -> str:
    """
    Receives the device name and makes a search in the smart_gsm website returning all the device info.

    Args:
        model (str): only the device model, without extra text.

    Returns:
        str: all the device specifications to be tell to the user
    """
    if model:
        return await smart_gsm.get_device(self, query = model)
    else: return "No se encontraron argumentos de busqueda. por favor pidele al usuario qué quiere buscar."


async def process_function_argument(response):
    arguments_list = []
    async for response_item in response:
        try:
            arguments_value = response_item.choices[0].delta.function_call.get("arguments", "")
            if arguments_value is not None: arguments_list.append(arguments_value)
            if response_item.choices[0].delta.get("finish_reason") == "function_call": break
        except: continue
    # Now that we have the list of argument fragments, join them into a single string
    if not arguments_list: return None
    arguments_str = "".join(arguments_list)
    # Now that we have the complete JSON string, we can parse it
    try:
        arguments = json.loads(arguments_str)
        return arguments
    except json.JSONDecodeError:
        print(f"Failed to parse JSON string: {arguments_str}")
        return None, None

async def handle_response_item(self, response, fn, usar_funciones, kwargs):
    function_name = ""
    async for response_item in response:
        if usar_funciones and response_item.choices[0].delta.get("function_call"):
            if not function_name:
                function_name = response_item.choices[0].delta.function_call.get("name")
            arguments = await process_function_argument(response)
            if arguments:
                function_response = await globals()[function_name](self, **arguments)
                new_dialog_message = {'function': f'{function_name}', "func_cont": f'{function_response}', "date": datetime.now()}
                from bot.src.utils.misc import update_dialog_messages
                _, _, tokencount = await update_dialog_messages(self.chat, new_dialog_message)
                kwargs["messages"].append({
                    "role": "function",
                    "name": f'{function_name}',
                    "content": f'{function_response}',
                })
                self.diccionario["max_tokens"] = tokencount
                self.diccionario["messages"] = kwargs["messages"]
            self.diccionario.pop("functions")
            self.diccionario.pop("function_call")
            await sleep(0.254)
            new_response = await fn(stream=True, **self.diccionario)
            async for new_response_item in new_response:
                self.answer += new_response_item.choices[0].delta.get("content", "")
                yield "not_finished", self.answer
        else:
            self.answer += response_item.choices[0].delta.get("content", "")
            yield "not_finished", self.answer


async def _openai(self, **kwargs):
    try:
        if self.proxies is not None:
            openai.proxy = {f'{proxy_raw.split("://")[0]}': f'{proxy_raw}'}

        api_info = api["info"].get(self.api, {})
        openai.api_key = str(api_info.get("key", ""))
        openai.api_base = str(api["info"][self.api].get("url"))
        if kwargs["messages"] != None:
            self.diccionario.update({"messages": kwargs["messages"], "model": self.model})
            if usar_funciones:
                self.diccionario["functions"] = await get_openai_funcs()
                self.diccionario["function_call"] = "auto"
            fn = openai.ChatCompletion.acreate
        else:
            self.diccionario.update({"prompt": kwargs["prompt"], "engine": self.model})
            fn = openai.Completion.acreate
        response = await fn(stream=True, **self.diccionario)
        async for response_status, answer in handle_response_item(self, response, fn, usar_funciones, kwargs):
            yield response_status, answer
    except Exception as e:
        print(e)
        raise ConnectionError(f'_get_openai_answer: {e}')

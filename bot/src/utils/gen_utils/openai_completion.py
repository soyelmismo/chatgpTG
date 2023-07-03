import openai
import json
from datetime import datetime
from .openai_functions_extraction import get_openai_funcs
from bot.src.utils.config import api, proxy_raw, usar_funciones
from bot.src.apis import duckduckgo, smart_gsm, wttr
from .openai_functions_extraction import openaifunc

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

@openaifunc
async def lookup_weather(self, location: str, unit: str) -> str:
    """
    Search actual weather info.

    Args:
        location (str): the city. mandatory.
        unit: "C" or "F". mandatory, and depends of the city

    Returns:
        str: all the weather info to be tell to the user
    """
    if location:
        return await wttr.getweather(location = location, unit = unit)
    else: return "No se encontraron argumentos de busqueda. por favor pidele al usuario qué quiere buscar."

@openaifunc
async def what_day_is(self) -> str:
    """
    Check the current date if the user asks

    Returns:
        str: the actual time
    """
    return str(datetime.now().strftime("%A, %B %d, %Y"))

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
    # Now that we have the complete JSON string, we can parse it
    arguments = json.loads("".join(arguments_list))
    return arguments

async def handle_response_item(self, old_response, fn, kwargs):
    function_name = ""
    arguments = None
    if self.diccionario.get("stream") == False:
        if hasattr(old_response.choices[0], "message") and "function_call" in old_response.choices[0].message:
            function_name = old_response.choices[0].message.function_call.get("name")
            arguments = json.loads(old_response.choices[0].message.function_call.get("arguments"))
    else:
        async for response_item in old_response:
            if hasattr(response_item.choices[0], "delta") and "function_call" in response_item.choices[0].delta:
                if not function_name:
                    function_name = response_item.choices[0].delta.function_call.get("name")
                arguments = await process_function_argument(old_response)
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
    response = await fn(**self.diccionario)
    if self.diccionario.get("stream") == False:
        yield None, eval(self.iter)
    else:
        async for response_item in response:
            self.answer += eval(self.iter)
            yield "not_finished", self.answer

async def _openai(self, **kwargs):
    try:
        if self.proxies is not None:
            openai.proxy = {f'{proxy_raw.split("://")[0]}': f'{proxy_raw}'}

        api_info = api["info"].get(self.api, {})
        openai.api_key = str(api_info.get("key", ""))
        openai.api_base = str(api["info"][self.api].get("url"))
        self, fn = await last_config(self, kwargs)
        response = await fn(**self.diccionario)
        if usar_funciones:
            async for response_status, answer in handle_response_item(self, response, fn, kwargs):
                yield response_status, answer
        else:
            if self.diccionario.get("stream") == False:
                yield None, eval(self.iter)
            else:
                async for response_item in response:
                    self.answer += eval(self.iter)
                    yield "not_finished", self.answer
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
            self.diccionario["functions"] = await get_openai_funcs()
            self.diccionario["function_call"] = "auto"
        fn = openai.ChatCompletion.acreate
    else:
        self.diccionario.update({"prompt": kwargs["prompt"], "engine": self.model})
        fn = openai.Completion.acreate

    return self, fn
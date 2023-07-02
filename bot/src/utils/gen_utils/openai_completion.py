import openai
import asyncio
import json
import re
from bot.src.apis import duckduckgo
from bot.src.utils.gen_utils.openai_decorator.openai_decorator import openaifunc, get_openai_funcs
from bot.src.utils.config import api, proxy_raw

usar_funciones = False


@openaifunc
async def web_search(query: str) -> str:
    """
    Internet access.
    Matches: "who is" "search" "research"...
    Search information on the web.
    @param query: the text / query that will be searched on the internet
    """
    print("buscando en internet...")
    if query:
        return await duckduckgo.search(query=query)
    else: return "No se encontraron argumentos de busqueda. por favor pidele al usuario qué quiere buscar."


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
                self.diccionario["functions"] = get_openai_funcs()
                self.diccionario["function_call"] = "auto"
            fn = openai.ChatCompletion.acreate
        else:
            self.diccionario.update({"prompt": kwargs["prompt"], "engine": self.model})
            fn = openai.Completion.acreate
        response = await fn(stream=True, **self.diccionario)
        arguments_str = ""
        arguments = {}
        function_name = ""
        async for response_item in response:
            if usar_funciones:
                function_call = response_item.choices[0].delta.get("function_call", "")
                if function_call:
                    while response_item.choices[0].get("finish_reason", "") != "function_call":
                        print("detectó functioncall")
                        if not function_name:
                            if "name" in function_call:
                                print("capturando nombre de funcion")
                                function_name = function_call.get("name")
                        if "arguments" in response_item:
                            arguments_value = response_item.get("arguments")
                            print(f'arguments_value antes : {arguments_value}')
                            while not arguments_value:
                                print("esperando argumentos...")
                            try:
                                arguments_obj = json.loads(arguments_value)
                                escaped_arguments = json.dumps(arguments_obj)
                                arguments_str += escaped_arguments
                            except:
                                print("error uniendo")
                                arguments_str += arguments_value
                            print("hay argumentos!", "sin escapar:" , function_call['arguments'], "escapado",arguments_str)
                    arguments = json.loads(arguments_str)
                    # Maneja la respuesta de llamada a funciones
                    print("debe llamar a una función")
                    print("funcion arguments",arguments)
                    function_response = await globals()[function_name](**arguments)
                    #function_response = await function_call(self, response_item)
                    print("recibió resultado", function_response)
                    # Haz algo con los resultados, por ejemplo, añádelos a la respuesta
                    from datetime import datetime
                    new_dialog_message = {'function': f'{function_name}', "content": f'{function_response}', "date": datetime.now()}
                    from bot.src.utils.misc import update_dialog_messages
                    _, _ = await update_dialog_messages(self.chat, new_dialog_message)
                    kwargs["messages"].append({
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    })
                    self.diccionario.update({"messages": kwargs["messages"]})
                    print(self.diccionario,"<<<<< resultados")
                    new_response = await fn(stream=True, **self.diccionario)
                    async for new_response_item in new_response:
                        print(f"response_item que deberia estar con info de la funcion {new_response_item}")
                        if kwargs['messages'] != None:
                            self.answer += new_response_item.choices[0].delta.get("content", "")
                        else:
                            self.answer += new_response_item.choices[0].text
                        yield "not_finished", self.answer
            else:
                if response_item.choices[0].finish_reason == "stop":
                    yield "finished", self.answer
                    break
                # Maneja la respuesta normalmente
                if kwargs['messages'] != None:
                    
                    self.answer += response_item.choices[0].delta.get("content", "")
                else:
                    self.answer += response_item.choices[0].text
                yield "not_finished", self.answer
    except Exception as e:
        print(e)
        raise ConnectionError(f'_get_openai_answer: {e}')

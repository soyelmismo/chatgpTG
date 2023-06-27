from bot.src.utils import config
import asyncio
from bot.src.utils.gen_utils.extrapis import duckduckgo
import openai
from bot.src.utils.gen_utils.openai_decorator.openai_decorator import openaifunc, get_openai_funcs
import json
import re
import aiohttp

usar_funciones = False

async def _make_api_call(self, **kwargs):
    self.answer = ""
    api_functions = {
        "chatbase": _chatbase,
        "g4f": _g4f,
        "you": _you,
        "evagpt4": _evagpt4
    }
    api_function = api_functions.get(self.api, _openai)
    for attempt in range(1, (config.max_retries) + 1):
        try:
            # Crea un iterador asincrónico
            api_iterator = api_function(self, **kwargs).__aiter__()

            # Espera el primer paquete con un tiempo de espera
            first_packet = await asyncio.wait_for(api_iterator.__anext__(), timeout=config.request_timeout)

            # Si el primer paquete se recibe con éxito, continúa con el resto de la respuesta
            yield first_packet
            async for status, self.answer in api_iterator:
                yield status, self.answer
            break # Si la llamada a la API fue exitosa, salimos del bucle
        except aiohttp.client_exceptions.ClientConnectionError: None
        except asyncio.exceptions.TimeoutError: None
        except Exception as e:
            if isinstance(e, asyncio.TimeoutError): None
            if attempt < config.max_retries: await asyncio.sleep(1.75)
            else: # Si hemos alcanzado el máximo número de reintentos, lanzamos la excepción
                error = f'{config.lang[self.lang]["errores"]["reintentos_alcanzados"].format(reintentos=config.max_retries)}'
                yield "error", f'{error}'
                raise ConnectionError(f"_make_api_call. {error}: {e}")

@openaifunc
async def research_internet(query: str) -> str:
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
        try:
            from bot.src.utils.gen_utils import middleware
            reqr = await middleware.resetip(self)
            print(reqr)
        except ImportError: pass

        api_info = config.api["info"].get(self.api, {})
        openai.api_key = str(api_info.get("key", ""))
        openai.api_base=str(config.api["info"][self.api].get("url"))
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
        #arguments_str = ""
        #arguments = {}
        async for response_item in response:
            # function_call = response_item.choices[0].delta.get("function_call", "")
            # if function_call:
            #     print("detectó functioncall")
            #     function_name = function_call["name"]
            #     print("nombre de la funcion",function_name)
            #     # Verifica si el mensaje es una llamada a la función
            #     try:
            #         print(function_call)
            #         if 'arguments' in function_call:
            #             arguments_str += function_call['arguments']
            #             print("hay argumentos!",function_call['arguments'])
            #     except Exception as e:
            #         print("MIERDa",e)
            #     arguments = json.loads(arguments_str)
            #     # Maneja la respuesta de llamada a funciones
            #     print("debe llamar a una función")
            #     print("funcion arguments",arguments)
            #     function_response = await globals()[function_name](**arguments)
            #     #function_response = await function_call(self, response_item)
            #     print("recibió resultado", function_response)
            #     # Haz algo con los resultados, por ejemplo, añádelos a la respuesta
            #     from datetime import datetime
            #     new_dialog_message = {'function': f'{function_name}', "content": f'{function_response}', "date": datetime.now()}
            #     from bot.src.utils.misc import update_dialog_messages
            #     _, _ = await update_dialog_messages(self.chat, new_dialog_message)
            #     kwargs["messages"].append({
            #         "role": "function",
            #         "name": function_name,
            #         "content": function_response,
            #     })
            #     self.diccionario.update({"messages": kwargs["messages"]})
            #     print(self.diccionario,"<<<<< resultados")
            #     new_response = await fn(stream=True, **self.diccionario)
            #     async for new_response_item in new_response:
            #         print(f"response_item que deberia estar con info de la funcion {new_response_item}")
            #         if kwargs['messages'] != None:
            #             self.answer += new_response_item.choices[0].delta.get("content", "")
            #         else:
            #             self.answer += new_response_item.choices[0].text
            #         yield "not_finished", self.answer
            # else:
                # Maneja la respuesta normalmente
                if kwargs['messages'] != None:
                    self.answer += response_item.choices[0].delta.get("content", "")
                else:
                    self.answer += response_item.choices[0].text
                yield "not_finished", self.answer
    except Exception as e:
        print(e)
        raise ConnectionError(f'_get_openai_answer: {e}')

async def _you(self, **kwargs):
    try:
        from bot.src.apis.gpt4free.foraneo import you
        r = you.Completion.create(
            prompt=kwargs['messages'],
            detailed=False,
            include_links=False
        )
        for chunk in r.text.encode('utf-16', 'surrogatepass').decode('utf-16'):
            self.answer += chunk
            if "Unable to fetch the response, Please try again." in self.answer:
                raise RuntimeError(self.answer)
            yield "not_finished", self.answer
    except Exception as e:
        e = f'_get_you_answer: {e}'
        raise ConnectionError(e)
        
async def _chatbase(self, **kwargs):
    try:
        from bot.src.apis.opengpt import chatbase
        r = chatbase.GetAnswer(messages=kwargs['messages'], model=self.model)
        for chunk in r:
            self.answer += chunk
            if "API rate limit exceeded" in self.answer:
                raise RuntimeError(config.lang[self.lang]["errores"]["utils_chatbase_limit"])
            yield "not_finished", self.answer
    except Exception as e:
        e = f'_get_chatbase_answer: {e}'
        raise ConnectionError(e)
async def _evagpt4(self, **kwargs):
    try:
        from bot.src.apis.opengpt import evagpt4
        r = evagpt4.Model(model=self.model).ChatCompletion(messages=kwargs['messages'])
        for chunk in r:
            self.answer += chunk
            yield "not_finished", self.answer
    except Exception as e:
        e = f'_get_evagpt4_answer: {e}'
        raise ConnectionError(e)
    
async def _g4f(self, **kwargs):
    try:
        from bot.src.apis.gpt4free import g4f
        provider_name = config.model['info'][self.model]['name']
        provider = getattr(g4f.Providers, provider_name)
        r = g4f.ChatCompletion.create(provider=provider, model='gpt-3.5-turbo', messages=kwargs['messages'])
        for chunk in r:
            self.answer += chunk
            yield "not_finished", self.answer
    except Exception as e:
        e = f'_get_g4f_answer: {e}'
        raise ConnectionError(e)
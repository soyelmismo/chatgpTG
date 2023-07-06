from bot.src.utils import config
import asyncio
import aiohttp
from .openai.openai_completion import _openai

async def _make_api_call(self, **kwargs):
    self.answer = ""
    api_functions = {
        "chatbase": _generic_create,
        "you": _you,
        "evagpt4": _generic_create,
        "chatllama": _generic_create,
        "chatgptai": _generic_create,
        "aichat": _generic_create
    }
    request_timeout = config.request_timeout
    if config.usar_streaming == False:
        request_timeout = request_timeout * 5
    api_function = api_functions.get(self.api, _openai)
    for attempt in range(1, (config.max_retries) + 1):
        try:
            # Crea un iterador asincrónico
            api_iterator = api_function(self, **kwargs).__aiter__()

            # Espera el primer paquete con un tiempo de espera
            first_packet = await asyncio.wait_for(api_iterator.__anext__(), timeout=request_timeout)

            # Si el primer paquete se recibe con éxito, continúa con el resto de la respuesta
            yield first_packet
            async for status, self.answer in api_iterator:
                yield status, self.answer
            break # Si la llamada a la API fue exitosa, salimos del bucle
        except (aiohttp.client_exceptions.ClientConnectionError, asyncio.exceptions.TimeoutError, asyncio.TimeoutError): None
        except Exception as e:
            if attempt < config.max_retries: await asyncio.sleep(1.75)
            else: # Si hemos alcanzado el máximo número de reintentos, lanzamos la excepción
                #yield "error", f'{config.lang[self.lang]["errores"]["reintentos_alcanzados"].format(reintentos=config.max_retries)}'
                raise ConnectionError(f'_make_api_call. {config.lang[config.pred_lang]["errores"]["reintentos_alcanzados"].format(reintentos=config.max_retries)}: {e}')

async def _you(self, **kwargs):
    try:
        from bot.src.apis.gpt4free.foraneo import you
        r = you.Completion.create(
            prompt=kwargs["messages"],
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

async def _generic_create(self, **kwargs):
    try:

        if self.api == "evagpt4":
            self.diccionario["messages"] = kwargs["messages"]
            from bot.src.apis.opengpt.evagpt4 import create
        elif self.api == "chatbase":
            # This have some rate limit too for a while.
            self.config = config
            self.diccionario["messages"] = kwargs["messages"]
            from bot.src.apis.opengpt.chatbase import create
        elif self.api == "chatgptai":
            self.diccionario["messages"] = kwargs["messages"]
            from bot.src.apis.opengpt.chatbase import create
        elif self.api == "chatllama":
            self.diccionario["prompt"] = kwargs["prompt"]
            from bot.src.apis.opengpt.chatllama import create
        elif self.api == "aichat":
            # This only have 10 requests... idk if per day lol...
            self.config = config
            self.diccionario["message"] = kwargs["prompt"]
            from bot.src.apis.gpt4free.aichat import create

        async for _, content in create(self):
            self.answer += content
            yield "not_finished", self.answer

    except Exception as e:
        raise ConnectionError(f"_generic_create {self.api}: {e}")

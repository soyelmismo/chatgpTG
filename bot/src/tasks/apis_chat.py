from types import SimpleNamespace
from bot.src.utils import config
from bot.src.utils.gen_utils.make_completion import _make_api_call
from bot.src.utils.preprocess.make_messages import handle as mms
from bot.src.utils.preprocess.make_prompt import handle as mpm
from bot.src.utils.constants import logger

vivas = config.api["available_api"]
malas = []
temp_malas = []
temp_vivas = []

async def checar_api(nombre_api):
    global temp_malas
    pseudo_self = SimpleNamespace()
    pseudo_self.api = nombre_api
    pseudo_self.lang = "en"
    pseudo_self.model = config.api["info"][nombre_api]["available_model"][0]
    pseudo_self.proxies = config.apisproxy
    pseudo_self.diccionario = {}
    pseudo_self.diccionario.clear()
    pseudo_self.diccionario.update(config.completion_options)
    pseudo_self.diccionario["stream"] = config.usar_streaming
    pseudo_self.diccionario["max_tokens"] = 800
    _message = "say pong"
    chat_mode = "nada"
    messages, prompt = (await mms(self=pseudo_self, _message=_message, chat_mode=chat_mode), None) if pseudo_self.model not in config.model["text_completions"] else (None, await mpm(self=pseudo_self, _message="say pong", chat_mode=chat_mode))
    kwargs = {
        "prompt": prompt,
        "messages": messages,
        "_message": _message
    }
    respuesta = ""
    try:
        rep = _make_api_call(pseudo_self, **kwargs)
        await rep.asend(None)
        async for _, answer in rep:
            respuesta += answer
        if respuesta:
            return respuesta
        return ["No"]
    except Exception as e:
        logger.error(f'{config.lang[config.pred_lang]["metagen"]["api"]}: {nombre_api}, {respuesta}, {e}')
        temp_malas.append(nombre_api)

async def checar_respuesta(nombre_api, respuesta):
    global temp_vivas
    global temp_malas
    if isinstance(respuesta, str) and "pong" in respuesta.lower():
        temp_vivas.append(nombre_api)
    else:
        temp_malas.append(nombre_api)

async def task():
    from bot.src.utils.proxies import sleep, asyncio
    global vivas
    global malas
    global temp_vivas
    global temp_malas
    test=False
    while True:
        logger.info("🔍🔌🌐🔄")
        try:
            temp_vivas = []
            temp_malas
            if test != True:
                for nombre_api in vivas:
                    respuesta = await checar_api(nombre_api)
                    await checar_respuesta(nombre_api, respuesta)
                temp_vivas = set(temp_vivas)
                temp_malas = set(temp_malas)
                vivas = set(vivas)
            else:
                temp_vivas = vivas
            if temp_vivas != vivas:
                from bot.src.utils.misc import api_check_text_maker
                outp = await api_check_text_maker(type="chat", vivas=vivas, temp_vivas=temp_vivas, temp_malas=temp_malas)
                logger.info(outp)
            else:
                logger.info("CHAT_APIS ✅")
            vivas = list(temp_vivas)
            malas = list(temp_malas)
        except asyncio.CancelledError:
            break
        await sleep(20 * 60)

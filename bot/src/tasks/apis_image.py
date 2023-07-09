from types import SimpleNamespace
from bot.src.utils import config
from bot.src.utils.gen_utils.make_image import gen as imagen
from bot.src.utils.constants import logger

img_vivas = config.api["available_image_api"]
img_malas = []
img_temp_malas = []
img_temp_vivas = []

async def checar_api(nombre_api):
    global img_temp_malas
    pseudo_self = SimpleNamespace()
    pseudo_self.proxies = config.apisproxy
    respuesta = ""
    try:
        image_urls, _ = await imagen(pseudo_self, "a beautiful EGG", nombre_api, "NO_STYLE", None, None, None, None)
        if image_urls:
            img_temp_vivas.append(nombre_api)
        else:
            img_temp_malas.append(nombre_api)
    except Exception as e:
        logger.error(f'{config.lang[config.pred_lang]["metagen"]["image_api"]}: {nombre_api}, {respuesta}, {e}')
        img_temp_malas.append(nombre_api)

async def task():
    from bot.src.utils.proxies import sleep, asyncio
    global img_vivas
    global img_malas
    global img_temp_vivas
    global img_temp_malas
    test=False
    while True:
        try:
            img_temp_vivas = []
            img_temp_malas = []
            if test != True:
                for nombre_api in img_vivas:
                    await checar_api(nombre_api)
                img_temp_vivas = set(img_temp_vivas)
                img_temp_malas = set(img_temp_malas)
                img_vivas = set(img_vivas)
            else:
                img_temp_vivas = img_vivas
            if img_temp_vivas != img_vivas:
                from bot.src.utils.misc import api_check_text_maker
                outp = await api_check_text_maker(type="img", vivas=img_vivas, temp_vivas=img_temp_vivas, temp_malas=img_temp_malas)
                logger.info(outp)
            else:
                logger.info("IMAGE_APIS ✅")
            img_vivas = list(img_temp_vivas)
            img_malas = list(img_temp_malas)
        except asyncio.CancelledError:
            break
        await sleep(20 * 60)

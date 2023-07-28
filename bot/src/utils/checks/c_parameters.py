from secrets import randbelow
from udatetime import now
from bot.src.utils.constants import (logger, constant_db_model, constant_db_chat_mode, constant_db_api,
                                     constant_db_image_api, constant_db_image_api_styles, image_api_styles, constant_db_imaginepy_ratios,
                                     constant_db_imaginepy_styles, imaginepy_ratios,
                                     imaginepy_styles, imaginepy_models, constant_db_imaginepy_models, constant_db_stablehorde_models, stablehorde_models)

async def check_attribute(chat, available, cache, db_attribute, update, error_message, atributos, stablehorde_workaround = None):
    try:
        from bot.src.utils.proxies import db
        current = cache[chat.id][0] if chat.id in cache else atributos[db_attribute]
        aviso = None
        if stablehorde_workaround:
            currente = available.get(int(current), None)
            #print("current og database", current)
            if not currente:
                #print("valores", available)
                #print("actual", current)
                #print("se activó aviso")
                aviso = True
        else:
            if current not in available:
                aviso = True

        if aviso:
            current = available[randbelow(len(available))]
            cache[chat.id] = (current, now())
            await db.set_chat_attribute(chat, db_attribute, current)
            await update.effective_chat.send_message(error_message.format(new=current))

        if cache.get(chat.id) is None or cache.get(chat.id)[0] != current: 
            cache[chat.id] = (current, now())
        return current
    except Exception as e:
        logger.error(f'<parameters_check_attribute> {available} | {cache} | {db_attribute} <-- {e}')

async def check(chat, lang, update):
    from bot.src.tasks.apis_chat import vivas as apis_vivas
    from bot.src.tasks.apis_image import img_vivas
    from bot.src.utils.proxies import db, chat_mode_cache, api_cache, model_cache, image_api_cache, image_api_styles_cache, config, imaginepy_ratios_cache, imaginepy_styles_cache, imaginepy_models_cache, stablehorde_models_cache
    db_attributes = [
        constant_db_chat_mode,
        constant_db_api,
        constant_db_image_api,
        constant_db_model,
        constant_db_image_api_styles,
        constant_db_stablehorde_models
    ]
    atributos = await db.get_chat_attributes_dict(chat, db_attributes)
    #print(f'{atributos}')
    checked_chat_mode = await check_attribute(
        chat, 
        config.chat_mode["available_chat_mode"], 
        chat_mode_cache, 
        constant_db_chat_mode, 
        update, 
        config.lang[lang]["errores"]["reset_chat_mode"],
        atributos
    )
    checked_api = await check_attribute(
        chat, 
        apis_vivas, 
        api_cache, 
        constant_db_api, 
        update, 
        config.lang[lang]["errores"]["reset_api"],
        atributos
    )
    checked_image_api = await check_attribute(
        chat, 
        img_vivas, 
        image_api_cache, 
        constant_db_image_api, 
        update, 
        config.lang[lang]["errores"]["reset_api"],
        atributos
    )
    checked_model = await check_attribute(
        chat, 
        config.api["info"][checked_api]["available_model"], 
        model_cache, 
        constant_db_model, 
        update, 
        config.lang[lang]["errores"]["reset_model"],
        atributos
    )
    checked_image_styles = await check_attribute(
        chat, 
        image_api_styles, 
        image_api_styles_cache, 
        constant_db_image_api_styles, 
        update, 
        config.lang[lang]["errores"]["reset_image_styles"],
        atributos
    )
    checked_stablehorde_models = await check_attribute(
        chat, 
        stablehorde_models, 
        stablehorde_models_cache, 
        constant_db_stablehorde_models, 
        update, 
        config.lang[lang]["errores"]["reset_imaginepy_models"],
        atributos,
        stablehorde_workaround = True
    )
    #print(f"devuelve current modelo {checked_stablehorde_models}")
    return checked_chat_mode, checked_api, checked_model, checked_image_api, checked_image_styles, None, checked_stablehorde_models

async def useless_atm(chat, lang, update):
    from bot.src.utils.proxies import config, imaginepy_ratios_cache, imaginepy_styles_cache, imaginepy_models_cache
    checked_imaginepy_styles = await check_attribute(
        chat, 
        imaginepy_styles, 
        imaginepy_styles_cache, 
        constant_db_imaginepy_styles, 
        update, 
        config.lang[lang]["errores"]["reset_imaginepy_styles"]
    )
    checked_imaginepy_ratios = await check_attribute(
        chat, 
        imaginepy_ratios, 
        imaginepy_ratios_cache, 
        constant_db_imaginepy_ratios, 
        update, 
        config.lang[lang]["errores"]["reset_imaginepy_ratios"]
    )
    checked_imaginepy_models = await check_attribute(
        chat, 
        imaginepy_models, 
        imaginepy_models_cache, 
        constant_db_imaginepy_models, 
        update, 
        config.lang[lang]["errores"]["reset_imaginepy_models"]
    )
    return checked_imaginepy_styles, checked_imaginepy_ratios, checked_imaginepy_models
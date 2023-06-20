import secrets
from bot.src.utils.constants import constant_db_model, constant_db_chat_mode, constant_db_api, constant_db_image_api, constant_db_imaginepy_ratios, constant_db_imaginepy_styles, imaginepy_ratios, imaginepy_styles

async def check_attribute(chat, attribute, available, cache, db_attribute, lang, update, error_message):
    from bot.src.utils.proxies import datetime, db, config
    current = cache[chat.id][0] if chat.id in cache else await db.get_chat_attribute(chat, db_attribute)
    if current not in available:
        current = available[secrets.randbelow(len(available))]
        cache[chat.id] = (current, datetime.now())
        await db.set_chat_attribute(chat, db_attribute, current)
        await update.effective_chat.send_message(error_message.format(new=current))
    if cache.get(chat.id) is None or cache.get(chat.id)[0] != current: 
        cache[chat.id] = (current, datetime.now())
    return current

async def check(chat, lang, update):
    from bot.src.utils.proxies import chat_mode_cache, api_cache, model_cache, image_api_cache, config, imaginepy_ratios_cache, imaginepy_styles_cache
    checked_chat_mode = await check_attribute(
        chat, 
        'chat_mode', 
        config.chat_mode["available_chat_mode"], 
        chat_mode_cache, 
        constant_db_chat_mode, 
        lang, 
        update, 
        config.lang["errores"]["reset_chat_mode"][lang]
    )
    checked_api = await check_attribute(
        chat, 
        'api', 
        config.api["available_api"], 
        api_cache, 
        constant_db_api, 
        lang, 
        update, 
        config.lang["errores"]["reset_api"][lang]
    )
    checked_image_api = await check_attribute(
        chat, 
        'image_api', 
        config.api["available_image_api"], 
        image_api_cache, 
        constant_db_image_api, 
        lang, 
        update, 
        config.lang["errores"]["reset_api"][lang]
    )
    checked_model = await check_attribute(
        chat, 
        'model', 
        config.api["info"][checked_api]["available_model"], 
        model_cache, 
        constant_db_model, 
        lang, 
        update, 
        config.lang["errores"]["reset_model"][lang]
    )
    checked_imaginepy_styles = await check_attribute(
        chat, 
        'imaginepy_styles', 
        imaginepy_styles, 
        imaginepy_styles_cache, 
        constant_db_imaginepy_styles, 
        lang, 
        update, 
        config.lang["errores"]["reset_imaginepy_styles"][lang]
    )
    checked_imaginepy_ratios = await check_attribute(
        chat, 
        'imaginepy_ratios', 
        imaginepy_ratios, 
        imaginepy_ratios_cache, 
        constant_db_imaginepy_ratios, 
        lang, 
        update, 
        config.lang["errores"]["reset_imaginepy_ratios"][lang]
    )
    return checked_chat_mode, checked_api, checked_model, checked_image_api, checked_imaginepy_styles, checked_imaginepy_ratios
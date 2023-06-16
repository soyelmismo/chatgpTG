import secrets
from bot.src.utils.constants import constant_db_model, constant_db_chat_mode, constant_db_api
async def check(chat, lang, update):
    from bot.src.utils.proxies import chat_mode_cache, api_cache, model_cache, apis_vivas, datetime, db, config
    # Verificar si hay valores inválidos en el usuario
    #chatmode
    mododechat_actual = (
        chat_mode_cache[chat.id][0] if chat.id in chat_mode_cache else
        await db.get_chat_attribute(chat, f'{constant_db_chat_mode}')
    )
    if mododechat_actual not in config.chat_mode["available_chat_mode"]:
        mododechat_actual = config.chat_mode["available_chat_mode"][1]
        chat_mode_cache[chat.id] = (mododechat_actual, datetime.now())
        await db.set_chat_attribute(chat, f'{constant_db_chat_mode}', mododechat_actual)
        await update.effective_chat.send_message(f'{config.lang["errores"]["reset_chat_mode"][lang].format(new=mododechat_actual)}')
    if chat_mode_cache.get(chat.id) is None or chat_mode_cache.get(chat.id)[0] != mododechat_actual: chat_mode_cache[chat.id] = (mododechat_actual, datetime.now())
    #api
    api_actual = (
        api_cache[chat.id][0] if chat.id in api_cache else
        await db.get_chat_attribute(chat, f'{constant_db_api}')
    )
    if not apis_vivas: raise LookupError(config.lang["errores"]["apis_vivas_not_ready_yet"][config.pred_lang])
    if api_actual not in apis_vivas:
        api_actual = apis_vivas[secrets.randbelow(len(apis_vivas) - 1)]
        api_cache[chat.id] = (api_actual, datetime.now())
        await db.set_chat_attribute(chat, f'{constant_db_api}', api_actual)
        await update.effective_chat.send_message(f'{config.lang["errores"]["reset_api"][lang].format(new=config.api["info"][api_actual]["name"])}')
    if api_cache.get(chat.id) is None or api_cache.get(chat.id)[0] != api_actual: api_cache[chat.id] = (api_actual, datetime.now())
    #model
    modelo_actual = (
        model_cache[chat.id][0] if chat.id in model_cache else
        await db.get_chat_attribute(chat, f'{constant_db_model}')
    )
    modelos_disponibles=config.api["info"][api_actual]["available_model"]
    if modelo_actual not in modelos_disponibles:
        api_actual = apis_vivas[secrets.randbelow(len(apis_vivas) - 1)]
        await db.set_chat_attribute(chat, f'{constant_db_model}', modelo_actual)
        await update.effective_chat.send_message(f'{config.lang["errores"]["reset_model"][lang].format(api_actual_name=config.api["info"][api_actual]["name"], new_model_name=config.model["info"][modelo_actual]["name"])}')
    if model_cache.get(chat.id) is None or model_cache.get(chat.id)[0] != modelo_actual: model_cache[chat.id] = (modelo_actual, datetime.now())
    return mododechat_actual, api_actual, modelo_actual
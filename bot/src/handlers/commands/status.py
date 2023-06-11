from bot.src.start import Update, CallbackContext
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import obtener_contextos as oc, db, ParseMode, config, model_cache, api_cache, chat_mode_cache
    chat, lang =  await oc(update, context)
    modelo_actual = model_cache[chat.id][0] if chat.id in model_cache else await db.get_chat_attribute(chat, 'current_model')
    api_actual = api_cache[chat.id][0] if chat.id in api_cache else await db.get_chat_attribute(chat, 'current_api')
    mododechat_actual = chat_mode_cache[chat.id][0] if chat.id in chat_mode_cache else await db.get_chat_attribute(chat, 'current_chat_mode')
    text = f'{config.lang["metagen"]["configuracion"][lang]}:\n\nAPI: {config.api["info"][api_actual]["name"]}.\n{config.lang["metagen"]["modelo"][lang]}: {config.model["info"][modelo_actual]["name"]}.\n{config.lang["metagen"]["chatmode"][lang]}: {config.chat_mode["info"][mododechat_actual]["name"][lang]}'
    await update.effective_chat.send_message(text, parse_mode=ParseMode.MARKDOWN)
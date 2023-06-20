from bot.src.start import Update, CallbackContext
from bot.src.utils.constants import constant_db_model, constant_db_chat_mode, constant_db_api, constant_db_tokens
async def handle(update: Update, context: CallbackContext, paraprops=None):
    from bot.src.utils.proxies import obtener_contextos as oc, db, ParseMode, config, model_cache, api_cache, chat_mode_cache
    chat, lang =  await oc(update)
    modelo_actual = model_cache[chat.id][0] if chat.id in model_cache else await db.get_chat_attribute(chat, f'{constant_db_model}')
    api_actual = api_cache[chat.id][0] if chat.id in api_cache else await db.get_chat_attribute(chat, f'{constant_db_api}')
    mododechat_actual = chat_mode_cache[chat.id][0] if chat.id in chat_mode_cache else await db.get_chat_attribute(chat, f'{constant_db_chat_mode}')
    tokens_actual = await db.get_dialog_attribute(chat, f'{constant_db_tokens}')

    nombreconfig=config.lang["metagen"]["configuracion"][lang]
    nombreapi=config.api["info"][api_actual]["name"]
    modelo=config.lang["metagen"]["modelo"][lang]
    nombremodelo=config.model["info"][modelo_actual]["name"]
    tokensmax=config.lang["metagen"]["tokensmax"][lang]
    modeltokens=config.model["info"][modelo_actual]["max_tokens"]
    chatmode=config.lang["metagen"]["chatmode"][lang]
    nombrechatmode=config.chat_mode["info"][mododechat_actual]["name"][lang]
    tokens=config.lang["metagen"]["tokens"][lang]
    textoprimer="""{nombreconfig}:\n\nAPI: {nombreapi}.\n{modelo}: {nombremodelo}.\n{tokensmax}: {modeltokens}.\n{chatmode}: {nombrechatmode}\n{tokens}: {tokens_actual}"""
    text = f'{textoprimer.format(nombreconfig=nombreconfig,nombreapi=nombreapi, modelo=modelo,nombremodelo=nombremodelo, tokensmax=tokensmax, modeltokens=modeltokens,chatmode=chatmode, nombrechatmode=nombrechatmode, tokens=tokens, tokens_actual=tokens_actual)}'
    if paraprops:
        return text
    await update.effective_chat.send_message(text, parse_mode=ParseMode.MARKDOWN)

from bot.src.start import Update, CallbackContext

import bot.src.handlers.menu as menu
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,logger,config,ParseMode)
    try:
        chat, _ = await oc(update)
        text, reply_markup = await menu.get(menu_type="lang", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f'<lang_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]} {e}')
async def callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await menu.handle(update)
    await menu.refresh(query, update, context, page_index, menu_type="lang")
async def set(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import obtener_contextos as oc,lang_cache, config
    chat, _ = await oc(update)
    query, _, seleccion, page_index, _ = await menu.handle(update)
    menu_type="lang"
    if seleccion in config.lang["available_lang"] and (lang_cache.get(chat.id) is None or lang_cache.get(chat.id)[0] != seleccion):
        await cambiar_idioma(update, chat, lang=seleccion)
    await menu.refresh(query, update, context, page_index, menu_type=menu_type, chat=chat)

async def cambiar_idioma(update, chat, lang):
    from bot.src.utils.proxies import (obtener_contextos as oc,lang_cache,db,config,datetime)
    if lang_cache.get(chat.id) is None or lang_cache.get(chat.id)[0] != lang:
        await db.set_chat_attribute(chat, "current_lang", lang)
        lang_cache[chat.id] = (lang, datetime.now())
        #await update.effective_chat.send_message(f'{config.lang["info"]["bienvenida"][lang]}')
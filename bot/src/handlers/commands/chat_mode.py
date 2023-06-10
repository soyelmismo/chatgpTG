from bot.src.start import Update, CallbackContext
import bot.src.handlers.menu as menu

async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,logger,config,ParseMode)
    try:
        chat, _ = await oc(update, context)
        text, reply_markup = await menu.get(menu_type="chat_mode", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError:
        logger.error(f'<chat_mode_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]}')
async def callback(update: Update, context: CallbackContext):
    query, page_index, _ = await menu.handle(update)
    await menu.refresh(query, update, context, page_index, menu_type="chat_mode")
async def set(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,chat_mode_cache,db,config,datetime,ParseMode)
    chat, lang = await oc(update, context)
    query, page_index, seleccion = await menu.handle(update)
    if seleccion != "paginillas" and (chat_mode_cache.get(chat.id) is None or chat_mode_cache.get(chat.id)[0] != seleccion):
        chat_mode_cache[chat.id] = (seleccion, datetime.now())
        await db.set_chat_attribute(chat, "current_chat_mode", seleccion)
        await update.effective_chat.send_message(f"{config.chat_mode['info'][seleccion]['welcome_message'][lang]}", parse_mode=ParseMode.HTML)
    await menu.refresh(query, update, context, page_index, menu_type="chat_mode", chat=chat)
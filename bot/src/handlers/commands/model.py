from bot.src.start import Update, CallbackContext
import bot.src.handlers.menu as menu
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,logger,config,ParseMode)
    try:
        chat, _ = await oc(update, context)
        text, reply_markup = await menu.get(menu_type="model", update=update, context=context,chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError:
        logger.error(f'<model_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]}')
async def callback(update: Update, context: CallbackContext):
    query, page_index, _ = await menu.handle(update)
    await menu.refresh(query, update, context, page_index, menu_type="model")
async def set(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,model_cache,db,datetime)
    chat, _ = await oc(update, context)
    query, page_index, seleccion = await menu.handle(update)
    if seleccion != "paginillas" and (model_cache.get(chat.id) is None or model_cache.get(chat.id)[0] != seleccion):
        model_cache[chat.id] = (seleccion, datetime.now())
        await db.set_chat_attribute(chat, "current_model", seleccion)
    await menu.refresh(query, update, context, page_index, menu_type="model", chat=chat)
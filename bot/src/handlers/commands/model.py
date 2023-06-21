from bot.src.start import Update, CallbackContext
import bot.src.handlers.menu as menu
from bot.src.utils.constants import constant_db_model
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,logger,config,ParseMode)
    try:
        chat, _ = await oc(update)
        text, reply_markup = await menu.get(menu_type="model", update=update, context=context,chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception as e: logger.error(f'{__name__}: <model_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]} {e}')
async def callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await menu.handle(update)
    await menu.refresh(query, update, context, page_index, menu_type="model")
async def set(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import obtener_contextos as oc,model_cache,db,datetime, config
    chat, _ = await oc(update)
    query, _, seleccion, page_index, _ = await menu.handle(update)
    menu_type="model"
    if seleccion in config.model["available_model"] and (model_cache.get(chat.id) is None or model_cache.get(chat.id)[0] != seleccion):
        model_cache[chat.id] = (seleccion, datetime.now())
        await db.set_chat_attribute(chat, f'{constant_db_model}', seleccion)
    await menu.refresh(query, update, context, page_index, menu_type=menu_type, chat=chat)
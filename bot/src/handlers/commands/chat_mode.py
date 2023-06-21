from bot.src.start import Update, CallbackContext
import bot.src.handlers.menu as menu
from bot.src.utils.constants import constant_db_chat_mode
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,logger,config,ParseMode)
    try:
        chat, _ = await oc(update)
        text, reply_markup = await menu.get(menu_type="chat_mode", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception as e: logger.error(f'{__name__}: <chat_mode_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]} {e}')
async def callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await menu.handle(update)
    await menu.refresh(query, update, context, page_index, menu_type="chat_mode")
async def set(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,chat_mode_cache,db,config,datetime,ParseMode)
    chat, lang = await oc(update)
    query, _, seleccion, page_index, _ = await menu.handle(update)
    menu_type="chat_mode"
    if seleccion in config.chat_mode["available_chat_mode"] and (chat_mode_cache.get(chat.id) is None or chat_mode_cache.get(chat.id)[0] != seleccion):
        chat_mode_cache[chat.id] = (seleccion, datetime.now())
        await db.set_chat_attribute(chat, f'{constant_db_chat_mode}', seleccion)
        await update.effective_chat.send_message(f"{config.chat_mode['info'][seleccion]['welcome_message'][lang]}", parse_mode=ParseMode.HTML)
    await menu.refresh(query, update, context, page_index, menu_type=menu_type, chat=chat)
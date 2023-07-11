from udatetime import now
from bot.src.start import Update, CallbackContext
from bot.src.handlers.menu import handle as hh, get as gg, refresh as rr
from bot.src.utils.constants import constant_db_chat_mode, logger
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,ParseMode,errorpredlang,menusnotready)
    try:
        chat, _ = await oc(update)
        text, reply_markup = await gg(menu_type="chat_mode", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception as e: logger.error(f'{__name__}: <chat_mode_handle> {errorpredlang}: {menusnotready} {e}')
async def callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await hh(update)
    await rr(query, update, context, page_index, menu_type="chat_mode")
async def set(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,chat_mode_cache,db,config,ParseMode)
    chat, lang = await oc(update)
    query, _, seleccion, page_index, _ = await hh(update)
    menu_type="chat_mode"
    if seleccion in config.chat_mode["available_chat_mode"] and (chat_mode_cache.get(chat.id) is None or chat_mode_cache.get(chat.id)[0] != seleccion):
        chat_mode_cache[chat.id] = (seleccion, now())
        await db.set_chat_attribute(chat, f'{constant_db_chat_mode}', seleccion)
        await update.effective_chat.send_message(f"{config.chat_mode['info'][seleccion]['welcome_message'][lang]}", parse_mode=ParseMode.HTML)
    await rr(query, update, context, page_index, menu_type=menu_type, chat=chat)
from udatetime import now
from bot.src.start import Update, CallbackContext
from bot.src.utils.constants import constant_db_api, logger
from bot.src.handlers.menu import handle as hh, get as gg, refresh as rr
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,ParseMode,errorpredlang,menusnotready)
    try:
        chat, _ = await oc(update)
        text, reply_markup = await gg(menu_type="api", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception as e: logger.error(f'{__name__}: <api_handle> {errorpredlang}: {menusnotready} {e}')

async def callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await hh(update)
    await rr(query, update, context, page_index, menu_type="api")

async def set(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import obtener_contextos as oc,api_cache,db
    from bot.src.tasks.apis_chat import vivas as apis_vivas
    chat, _ = await oc(update)
    query, _, seleccion, page_index, _ = await hh(update)
    menu_type="api"
    if seleccion in apis_vivas and (api_cache.get(chat.id) is None or api_cache.get(chat.id)[0] != seleccion):
        api_cache[chat.id] = (seleccion, now())
        await db.set_chat_attribute(chat, f'{constant_db_api}', seleccion)
    await rr(query, update, context, page_index, menu_type=menu_type, chat=chat)
from udatetime import now
from bot.src.start import Update, CallbackContext
from bot.src.utils.constants import logger
from bot.src.handlers.menu import handle as hh, get as gg, refresh as rr
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,ParseMode,errorpredlang,menusnotready)
    try:
        chat, _ = await oc(update)
        text, reply_markup = await gg(menu_type="lang", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception as e: logger.error(f'{__name__}: <lang_handle> {errorpredlang}: {menusnotready} {e}')
async def callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await hh(update)
    await rr(query, update, context, page_index, menu_type="lang")
async def set(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import obtener_contextos as oc,lang_cache, config
    chat, _ = await oc(update)
    query, _, seleccion, page_index, _ = await hh(update)
    menu_type="lang"
    if seleccion in config.available_lang and (lang_cache.get(chat.id) is None or lang_cache.get(chat.id)[0] != seleccion):
        await cambiar_idioma(None, chat, seleccion)
    await rr(query, update, context, page_index, menu_type=menu_type, chat=chat)

async def cambiar_idioma(update, chat, lang):
    from bot.src.utils.proxies import (lang_cache,db,config)
    from bot.src.utils.constants import constant_db_lang
    if lang_cache.get(chat.id) is None or lang_cache.get(chat.id)[0] != lang:
        await db.set_chat_attribute(chat, f'{constant_db_lang}', lang)
        lang_cache[chat.id] = (lang, now())
        if update:
            await update.effective_chat.send_message(f'{config.lang[lang]["info"]["bienvenida"]}')
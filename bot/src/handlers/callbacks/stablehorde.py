from udatetime import now
from bot.src.start import Update, CallbackContext
from bot.src.handlers.menu import handle as hh, get as gg, refresh as rr
from bot.src.utils.proxies import obtener_contextos as oc, config, db, stablehorde_models_cache,ParseMode,errorpredlang,menusnotready
from bot.src.utils.constants import constant_db_stablehorde_models, constant_db_image_api_styles, constant_db_imaginepy_models, logger, stablehorde_models

async def handle(update: Update, context: CallbackContext):
    try:
        chat, _ = await oc(update)
        text, reply_markup = await gg(menu_type="stablehorde", update=update, context=context,chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError: logger.error(f'{__name__}: <stablehorde_options_handle> {errorpredlang}: {menusnotready}')
async def callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await hh(update)
    await rr(query, update, context, page_index, menu_type="stablehorde")
async def set(update: Update, context: CallbackContext):
    chat, _ = await oc(update)
    query, propsmenu, seleccion, page_index, _ = await hh(update)
    menu_type = await admin_selecciones(propsmenu, seleccion, chat)
    await rr(query, update, context, page_index, menu_type=menu_type, chat=chat)

async def admin_selecciones(propsmenu, seleccion, chat):
    menu_type = "stablehorde"
    if menu_type == "stablehorde" and seleccion in config.props["stablehorde"]["available_options"]: menu_type=seleccion
    if propsmenu == "set_stablehorde_models":
        menu_type = "stablehorde_models"
        if seleccion != "paginillas":
            stablehorde_models_cache[chat.id] = (seleccion, now())
            await db.set_chat_attribute(chat, f'{constant_db_stablehorde_models}', seleccion)
    elif propsmenu == "set_image_api_styles":
        menu_type = "image_api_styles"
        if seleccion != "paginillas":
            constant_db_image_api_styles[chat.id] = (seleccion, now())
            await db.set_chat_attribute(chat, f'{constant_db_image_api_styles}', seleccion)
    return menu_type

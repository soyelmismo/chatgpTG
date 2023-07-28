from bot.src.start import Update, CallbackContext
from bot.src.handlers.menu import handle as hh, get as gg, refresh as rr
from bot.src.utils.checks.c_callback import check as is_this_shit_callback
from bot.src.utils.proxies import obtener_contextos as oc, config, errorpredlang, menusnotready, ParseMode
from bot.src.utils.constants import logger
async def handle(update: Update, context: CallbackContext):
    try:
        chat, _ = await oc(update)
        text, reply_markup = await gg(menu_type="props", update=update, context=context, chat=chat, page_index=0)
        await context.bot.send_message(chat_id=chat.id,text=text,reply_markup=reply_markup,parse_mode=ParseMode.HTML)

    except Exception as e: logger.error(f'{__name__}: <props_handle> {errorpredlang}: {menusnotready} {e}')
async def callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await hh(update)
    await rr(query, update, context, page_index, menu_type="props")
async def set(update: Update, context: CallbackContext):
    chat, _ = await oc(update)
    query, _, seleccion, _, is_from_callback = await hh(update)
    menu_type = await admin_selecciones(update, context, seleccion, is_from_callback)
    await rr(query=query, update=update, context=context, page_index=0, menu_type=menu_type, chat=chat)

async def admin_selecciones(update, context, seleccion, is_from_callback):
    menu_type = seleccion  # Inicializamos menu_type con el valor de seleccion
    from_callback = await is_this_shit_callback(is_from_callback)
    if seleccion == "paginillas":
        if from_callback:
            if from_callback in ["stablehorde_models"]: menu_type = "stablehorde"
            elif from_callback in ["image_api_styles", "stablehorde"]: menu_type = "image_api"
            elif from_callback in config.props["available_props"]: menu_type = "props"
        else: menu_type = "props"  # Actualizamos menu_
    elif seleccion == "reset":
        from .reset import handle
        await handle(update, context, yey=True)
        menu_type = "props"  # Actualizamos menu_
    return menu_type
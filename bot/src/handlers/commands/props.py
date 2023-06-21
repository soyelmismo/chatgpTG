from bot.src.start import Update, CallbackContext
import bot.src.handlers.menu as menu
from bot.src.utils.checks.c_callback import check as is_this_shit_callback
from bot.src.utils.proxies import obtener_contextos as oc, config, logger, ParseMode
async def handle(update: Update, context: CallbackContext):
    try:
        chat, _ = await oc(update)
        text, reply_markup = await menu.get(menu_type="props", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception as e: logger.error(f'{__name__}: <props_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]} {e}')
async def callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await menu.handle(update)
    await menu.refresh(query, update, context, page_index, menu_type="props")
async def set(update: Update, context: CallbackContext):
    chat, _ = await oc(update)
    query, _, seleccion, _, is_from_callback = await menu.handle(update)
    menu_type = await admin_selecciones(update, context, seleccion, is_from_callback)
    await menu.refresh(query=query, update=update, context=context, page_index=0, menu_type=menu_type, chat=chat)

async def admin_selecciones(update, context, seleccion, is_from_callback):
    menu_type = seleccion  # Inicializamos menu_type con el valor de seleccion
    from_callback = await is_this_shit_callback(is_from_callback)
    if seleccion == "paginillas":
        if from_callback:
            if from_callback in config.props["imaginepy"]["available_options"]: menu_type = "imaginepy"
            elif from_callback == "imaginepy": menu_type = "image_api"
            elif from_callback in config.props["available_props"]: menu_type = "props"
        else: menu_type = "props"  # Actualizamos menu_
    elif seleccion == "reset":
        from .reset import handle
        await handle(update, context, yey=True)
        menu_type = "props"  # Actualizamos menu_
    return menu_type
from bot.src.start import Update, CallbackContext
import bot.src.handlers.menu as menu
from bot.src.utils.proxies import obtener_contextos as oc, config, db, imaginepy_ratios_cache, imaginepy_styles_cache, datetime,logger,ParseMode
from bot.src.utils.constants import constant_db_imaginepy_ratios, constant_db_imaginepy_styles

async def handle(update: Update, context: CallbackContext):
    try:
        chat, _ = await oc(update)
        text, reply_markup = await menu.get(menu_type="imaginepy", update=update, context=context,chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError: logger.error(f'<imaginepy_options_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]}')
async def callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await menu.handle(update)
    await menu.refresh(query, update, context, page_index, menu_type="imaginepy")
async def set(update: Update, context: CallbackContext):
    chat, _ = await oc(update)
    query, propsmenu, seleccion, page_index, _ = await menu.handle(update)
    menu_type = await admin_selecciones(propsmenu, seleccion, chat)
    await menu.refresh(query, update, context, page_index, menu_type=menu_type, chat=chat)

async def admin_selecciones(propsmenu, seleccion, chat):
    menu_type = "imaginepy"
    if menu_type == "imaginepy" and seleccion in config.props["imaginepy"]["available_options"]: menu_type=seleccion
    if propsmenu == "set_imaginepy_ratios":
        menu_type = "imaginepy_ratios"
        if seleccion != "paginillas":
            imaginepy_ratios_cache[chat.id] = (seleccion, datetime.now())
            await db.set_chat_attribute(chat, f'{constant_db_imaginepy_ratios}', seleccion)
    elif propsmenu == "set_imaginepy_styles":
        menu_type = "imaginepy_styles"
        if seleccion != "paginillas":
            imaginepy_styles_cache[chat.id] = (seleccion, datetime.now())
            await db.set_chat_attribute(chat, f'{constant_db_imaginepy_styles}', seleccion)
    return menu_type
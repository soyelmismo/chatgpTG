from bot.src.handlers import menu
from bot.src.utils.proxies import ParseMode, Update, CallbackContext, obtener_contextos as oc
async def imagine(update: Update, context: CallbackContext):
    chat, _ = await oc(update)
    text, reply_markup = await menu.get(menu_type="imaginepy_styles", update=update, context=context,chat=chat, page_index=0)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
from bot.src.handlers.menu import get
from bot.src.utils.proxies import ParseMode, Update, CallbackContext, obtener_contextos as oc, parametros
async def imagine(update: Update, context: CallbackContext):
    chat, lang = await oc(update)
    _, _, _, checked_image_api, _, _, _= await parametros(chat, lang, update)
    if checked_image_api == "imaginepy":
        text, reply_markup = await get(menu_type="imaginepy_styles", update=update, context=context,chat=chat, page_index=0)
        await update.effective_message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
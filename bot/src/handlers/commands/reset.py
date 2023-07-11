from bot.src.start import Update, CallbackContext
async def handle(update: Update, context: CallbackContext, yey=None):
    from bot.src.utils.proxies import obtener_contextos as oc, db, ParseMode
    chat, _ = await oc(update)
    await db.reset_chat_attribute(chat)
    if not yey:
        await update.effective_chat.send_message("Yey", parse_mode=ParseMode.HTML)
from bot.src.start import Update, CallbackContext
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import obtener_contextos as oc, db, ParseMode
    chat, _ = await oc(update)
    await db.reset_chat_attribute(chat)
    await update.effective_chat.send_message("Yey", parse_mode=ParseMode.HTML)
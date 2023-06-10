from bot.src.start import Update, CallbackContext
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import config, ParseMode, obtener_contextos as oc
    _, lang = await oc(update, context)
    reply_text = f'{config.lang["mensajes"]["mensaje_bienvenido"][lang]}🤖\n\n'
    reply_text += f'{config.lang["mensajes"]["mensaje_ayuda"][lang]}'
    await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)
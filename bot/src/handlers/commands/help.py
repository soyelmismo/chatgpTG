from bot.src.start import Update, CallbackContext

async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import config, ParseMode, obtener_contextos as oc
    _, lang = await oc(update, context)
    await update.message.reply_text(config.lang["mensajes"]["mensaje_ayuda"][lang], parse_mode=ParseMode.HTML)

async def group(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import config, ParseMode, obtener_contextos as oc
    _, lang = await oc(update, context)
    text = config.lang["mensajes"]["ayuda_grupos"][lang].format(bot_username="@" + context.bot.username)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    await update.message.reply_video(config.help_group_chat_video_path)
from bot.src.start import Update, CallbackContext

async def check(update, context):
    message=update.message
    try:
        return (True if message.chat.type == "private"
            or message.text is not None and ("@" + context.bot.username) in message.text
            or message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id
            else False)
    except AttributeError:
        return True
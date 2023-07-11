from bot.src.start import Update

async def check(update):
    chat = update.callback_query.message.chat if update.callback_query else update.effective_chat
    return chat
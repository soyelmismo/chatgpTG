from bot.src.start import Update

async def check(update):
    chat = update.effective_chat    
    return chat
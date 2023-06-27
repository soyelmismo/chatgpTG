from bot.src.start import Update, CallbackContext
from bot.src.handlers import semaphore as tasks
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (config, datetime, obtener_contextos as oc, debe_continuar, db, interaction_cache)
    chat, lang = await oc(update)
    if not await debe_continuar(chat, lang, update, context): return
    dialog_messages = await db.get_dialog_messages(chat, dialog_id=None)
    if len(dialog_messages) == 0:
        await tasks.releasemaphore(chat=chat)
        text = config.lang[lang]["mensajes"]["no_retry_mensaje"]
        await update.effective_chat.send_message(text)
        return
    last_dialog_message = dialog_messages.pop()
    await db.set_dialog_messages(chat, dialog_messages, dialog_id=None)  # last message was removed from the context
    interaction_cache[chat.id] = ("visto", datetime.now())
    await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    await tasks.releasemaphore(chat=chat)
    _message = last_dialog_message["user"]
    from bot.src.handlers.message import handle as messend
    await messend(chat, lang, update, context, _message)
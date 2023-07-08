from udatetime import now
from bot.src.start import Update, CallbackContext
from bot.src.handlers import semaphore as tasks
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (
    obtener_contextos as oc,
    config, ParseMode,
    interaction_cache, db, chat_locks, chat_tasks
    )
    chat, lang = await oc(update)
    lock = chat_locks.get(chat.id)
    if not lock and not lock.locked() or chat.id not in chat_tasks:
        text = config.lang[lang]["mensajes"]["nadacancelado"]
        await update.effective_chat.send_message(text, reply_to_message_id=update.effective_message.message_id, parse_mode=ParseMode.HTML)
    else:        
        await update.effective_chat.send_message(f'{config.lang[lang]["mensajes"]["cancelado"]}', reply_to_message_id=update.effective_message.message_id, parse_mode=ParseMode.HTML)
        task = chat_tasks.get(chat.id)
        if task is not None:
            task.cancel()
            await tasks.releasemaphore(chat)
            interaction_cache[chat.id] = ("visto", now())
            await db.set_chat_attribute(chat, "last_interaction", now())
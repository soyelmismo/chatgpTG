from bot.src.start import Update, CallbackContext
from bot.src.handlers import semaphore as tasks
async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (
    obtener_contextos as oc,
    config, datetime, ParseMode,
    interaction_cache, db, chat_locks, chat_tasks
    )
    chat, lang = await oc(update, context)
    lock = chat_locks.get(chat.id)
    if not lock and not lock.locked() or chat.id not in chat_tasks:
        text = config.lang["mensajes"]["nadacancelado"][lang]
        #type = update.callback_query.effective_chat if update.callback_query else update.effective_chat
        await update.effective_chat.send_message(text, reply_to_message_id=update.effective_message.message_id, parse_mode=ParseMode.HTML)
    else:
        task = chat_tasks[chat.id]
        task.cancel()
        await tasks.releasemaphore(chat)
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())

async def handle(chat, lang, task, update):
    from bot.src.utils.proxies import chat_locks, chat_tasks, config, logger, asyncio, ParseMode
    async with chat_locks[chat.id]:
        chat_tasks[chat.id] = task
        try:
            await acquiresemaphore(chat=chat)
            await task
        except asyncio.CancelledError:
            task.cancel()
            await update.effective_chat.send_message(f'{config.lang["mensajes"]["cancelado"][lang]}', parse_mode=ParseMode.HTML)
        except RuntimeError as e:
            if 'Event loop is closed' in str(e): logger.error("Error: el bucle de eventos ya finalizó")
        finally:
            await releasemaphore(chat)
            if chat.id in chat_tasks: del chat_tasks[chat.id]
async def acquiresemaphore(chat):
    from bot.src.utils.proxies import chat_locks, asyncio
    lock = chat_locks.get(chat.id)
    lock = asyncio.Lock() if lock is None else lock
    chat_locks[chat.id] = lock
    await lock.acquire()
async def releasemaphore(chat):
    from bot.src.utils.proxies import chat_locks
    lock = chat_locks.get(chat.id)
    lock.release() if lock and lock.locked() else None
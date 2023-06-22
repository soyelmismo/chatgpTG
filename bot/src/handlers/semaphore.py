from bot.src.utils.proxies import chat_locks, chat_tasks, config, logger, asyncio, ParseMode

async def handle(chat, lang, task, update):
    async with chat_locks[chat.id]:
        chat_tasks[chat.id] = task
        try:
            await acquiresemaphore(chat=chat)
            await task
        except asyncio.CancelledError:
            task.cancel()
            try: await update.effective_chat.send_message(f'{config.lang["mensajes"]["cancelado"][lang]}', parse_mode=ParseMode.HTML)
            except Exception as e: logger.error(f"{__name__}: Error al enviar el mensaje de cancelación: {e}")
        except Exception as e:
            if "access local variable 'answer' where" in e: None
            else: logger.error(f"{__name__}: Error: {e}")
        finally:
            await releasemaphore(chat)
            chat_tasks.pop(chat.id, None)

async def acquiresemaphore(chat):
    lock = chat_locks.get(chat.id)
    lock = asyncio.Lock() if lock is None else lock
    chat_locks[chat.id] = lock
    await lock.acquire()
async def releasemaphore(chat):
    lock = chat_locks.get(chat.id)
    lock.release() if lock and lock.locked() else None
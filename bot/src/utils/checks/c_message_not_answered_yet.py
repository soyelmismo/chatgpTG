async def check(chat, lang, update):
    from bot.src.utils.proxies import chat_locks, config, ParseMode
    lock = chat_locks.get(chat.id)
    if lock and lock.locked():
        text = f'{config.lang["mensajes"]["mensaje_semaforo"][lang]}'
        id = update.callback_query.message.message_id if update.callback_query else update.message.message_id if update.message else update.effective_message.message_id
        await update.effective_chat.send_message(text, reply_to_message_id=id, parse_mode=ParseMode.HTML)
        return True
    else:
        return False
async def check(chat, lang, update):
    from bot.src.utils.proxies import chat_locks, config, ParseMode
    lock = chat_locks.get(chat.id)
    if lock and lock.locked():
        text = f'{config.lang[lang]["mensajes"]["mensaje_semaforo"]}'
        # Extracted nested conditional into an independent statement
        if update.callback_query:
            msgid = update.callback_query.message.message_id
        elif update.message:
            msgid = update.message.message_id
        else:
            msgid = update.effective_message.message_id
        await update.effective_chat.send_message(text, reply_to_message_id=msgid, parse_mode=ParseMode.HTML)
        return True
    else:
        return False
async def check(update, _message=None):
    raw_msg = _message or update.effective_message
    if not isinstance(raw_msg, str): _message = raw_msg.text if raw_msg.text else raw_msg.reply_to_message.text
    return raw_msg, _message
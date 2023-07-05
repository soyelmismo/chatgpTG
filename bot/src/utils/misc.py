from .proxies import db, model_cache
from datetime import datetime
from .constants import constant_db_model, constant_db_tokens
from bot.src.utils.preprocess import tokenizer

async def send_large_message(text, update):
    from .proxies import ParseMode
    if len(text) <= 4096:
        await update.effective_chat.send_message(f'{text}', reply_to_message_id=update.effective_message.message_id, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
    else:
        # Divide el mensaje en partes más pequeñas
        message_parts = [text[i:i+4096] for i in range(0, len(text), 4096)]
        for part in message_parts:
            await update.effective_chat.send_message(f'{part}', reply_to_message_id=update.effective_message.message_id, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)

async def clean_text(doc, chat):
    max_tokens = await ver_modelo_get_tokens(chat)
    doc, tokencount, advertencia = await tokenizer.handle(input_data=doc, max_tokens=max_tokens)
    return doc, tokencount, advertencia

async def update_dialog_messages(chat, new_dialog_message=None):
    from .proxies import db
    dialog_messages = await db.get_dialog_messages(chat, dialog_id=None)
    max_tokens = await ver_modelo_get_tokens(chat)
    if new_dialog_message is not None: dialog_messages += [new_dialog_message]
    dialog_messages, tokencount, advertencia = await tokenizer.handle(input_data=dialog_messages, max_tokens=max_tokens)
    await db.set_dialog_messages(
        chat,
        dialog_messages,
        dialog_id=None
    )
    await db.set_dialog_attribute(chat, f'{constant_db_tokens}', int(tokencount))
    return advertencia, dialog_messages, int(tokencount)

async def ver_modelo_get_tokens(chat=None, model=None):
    if not model:
        model = model_cache[chat.id][0] if model_cache.get(chat.id) else await db.get_chat_attribute(chat, f'{constant_db_model}')
        model_cache[chat.id] = (model, datetime.now())
    from bot.src.utils.config import model as modelist
    max_tokens = int(modelist["info"][model]["max_tokens"])
    return max_tokens
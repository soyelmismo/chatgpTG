from .proxies import db, model_cache, datetime
from .constants import constant_db_model, constant_db_tokens

async def send_large_message(text, update):
    from .proxies import ParseMode
    if len(text) <= 4096:
        await update.effective_chat.send_message(f'{text}', reply_to_message_id=update.effective_message.message_id, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
        #await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    else:
        # Divide el mensaje en partes más pequeñas
        message_parts = [text[i:i+4096] for i in range(0, len(text), 4096)]
        for part in message_parts:
            await update.effective_chat.send_message(f'{part}', reply_to_message_id=update.effective_message.message_id, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
            #await update.message.reply_text(part, parse_mode=ParseMode.HTML)

from bot.src.utils.preprocess import remove_words

async def clean_text(doc, chat):
    from .proxies import re
    #patron = r"[^a-zA-Z0-9\s]|[^あ-んア-ン一-龯\s]|[^一-\u9FFF\s]|[^؀-ۿ\s]|[^á-úÁ-ÚñÑ\s]"
    doc = re.sub(r"[^a-zA-Z0-9\s]", '', doc)
    doc = re.sub(r'[\n\r]+', ' ', doc)  # Eliminar saltos de línea
    doc = re.sub(r' {2,}', ' ', doc)  # Eliminar dos o más espacios seguidos
    doc = doc.strip()  # Eliminar espacios en blanco al principio y final del string
    max_tokens = await ver_modelo_get_tokens(chat)
    doc, _ =await remove_words.handle(texto=f'{doc}', max_tokens=max_tokens) 
    return doc

async def update_dialog_messages(chat, new_dialog_message=None):
    from .proxies import db
    dialog_messages = await db.get_dialog_messages(chat, dialog_id=None)
    max_tokens = await ver_modelo_get_tokens(chat)
    dialog_messages, tokencount=await remove_words.handle(texto=dialog_messages, max_tokens=max_tokens)
    if new_dialog_message is not None: dialog_messages += [new_dialog_message]
    await db.set_dialog_messages(
        chat,
        dialog_messages,
        dialog_id=None
    )
    await db.set_dialog_attribute(chat, f'{constant_db_tokens}', int(tokencount))
    
async def ver_modelo_get_tokens(chat):
    model = model_cache[chat.id][0] if model_cache.get(chat.id) else await db.get_chat_attribute(chat, f'{constant_db_model}')
    model_cache[chat.id] = (model, datetime.now())
    from bot.src.utils.config import model as modelist
    max_tokens = int(modelist["info"][model]["max_tokens"])
    return max_tokens
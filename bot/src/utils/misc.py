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

async def clean_text(doc):
    from .proxies import re
    doc = re.sub(r'[\n\r]+', ' ', doc)  # Eliminar saltos de línea
    doc = re.sub(r' {2,}', ' ', doc)  # Eliminar dos o más espacios seguidos
    doc = doc.strip()  # Eliminar espacios en blanco al principio y final del string
    return doc

async def add_dialog_message(chat, new_dialog_message):
    from .proxies import db
    await db.set_dialog_messages(
        chat,
        await db.get_dialog_messages(chat, dialog_id=None) + [new_dialog_message],
        dialog_id=None
    )
from udatetime import now
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

async def ver_modelo_get_tokens(chat=None, model=None, api=None):
    try:
        from .proxies import db, model_cache
        if not model:
            model = model_cache[chat.id][0] if model_cache.get(chat.id) else await db.get_chat_attribute(chat, f'{constant_db_model}')
            model_cache[chat.id] = (model, now())

        from bot.src.utils.config import model as modelist, api as apilist
        if api and apilist["info"][api].get("api_max_tokens"):
            return int(apilist["info"][api]["api_max_tokens"])

        return int(modelist["info"][model]["max_tokens"])
    except Exception as e: raise ValueError(f'<ver_modelo_get_tokens> {e}')

async def api_check_text_maker(type: str = None, vivas: set = None, temp_vivas: set = None, temp_malas: set = None):
    from bot.src.utils import config
    if type == "img":
        init = config.lang[config.pred_lang]["metagen"]["image_api"]
    elif type == "chat":
        init = config.lang[config.pred_lang]["metagen"]["api"]

    check = config.lang[config.pred_lang]["apicheck"]["inicio"]
    totales = f'{config.lang[config.pred_lang]["apicheck"]["connection"]}: {len(temp_vivas)}, {config.lang[config.pred_lang]["apicheck"]["bad"]}: {len(temp_malas)}, {config.lang[config.pred_lang]["apicheck"]["total"]}: {len(vivas)}'
    tex_vivas = ""
    tex_malas = ""
    text = """{init}: {check}\n\n{totales}"""
    if temp_vivas:
        tex_vivas = f'{config.lang[config.pred_lang]["apicheck"]["working"]}: {temp_vivas}'
        text += "\n{vivas}"
    if temp_malas:
        tex_malas = f'{config.lang[config.pred_lang]["apicheck"]["dead"]}: {temp_malas}'
        text += "\n{malas}"
    return text.format(init=init, check=check, totales=totales, vivas=tex_vivas, malas=tex_malas)

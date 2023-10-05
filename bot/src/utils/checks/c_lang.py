from datetime import datetime
from bot.src.utils.constants import constant_db_lang
async def check(update, chat=None):
    if not chat:
        from bot.src.utils.checks import c_chat
        chat = await c_chat.check(update)
    from bot.src.utils.proxies import lang_cache, db, config
    if lang_cache.get(chat.id) is not None:
        lang = lang_cache[chat.id][0]
    elif await db.chat_exists(chat):
        lang = await db.get_chat_attribute(chat, constant_db_lang)
    elif update.effective_user.language_code in config.available_lang:
        lang = update.effective_user.language_code
    else:
        lang = str(config.pred_lang)
    lang_cache[chat.id] = (lang, datetime.now())
    return lang
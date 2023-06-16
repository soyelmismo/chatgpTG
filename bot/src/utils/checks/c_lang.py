from bot.src.start import Update

async def check(update, chat=None):
    from bot.src.utils.proxies import lang_cache, datetime, db, config
    if lang_cache.get(chat.id) is not None:
        lang = lang_cache[chat.id][0]
    elif await db.chat_exists(chat):
        lang = await db.get_chat_attribute(chat, "current_lang")
    elif update.effective_user.language_code in config.lang["available_lang"]:
        lang = update.effective_user.language_code
    else:
        lang = str(config.pred_lang)
    lang_cache[chat.id] = (lang, datetime.now())
    return lang
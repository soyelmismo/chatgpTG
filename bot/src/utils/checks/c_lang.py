from bot.src.start import Update

async def check(update, chat=None):
    from bot.src.utils.proxies import lang_cache, datetime, db, config
    lang = (lang_cache[chat.id][0] if lang_cache.get(chat.id) != None else
        await db.get_chat_attribute(chat, "current_lang") if await db.chat_exists(chat) else
        update.effective_user.language_code if update.effective_user.language_code in config.lang["available_lang"] else
        str(config.pred_lang))
    lang_cache[chat.id] = (lang, datetime.now())
    return lang
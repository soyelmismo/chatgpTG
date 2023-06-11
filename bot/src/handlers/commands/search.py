from bot.src.start import Update, CallbackContext
from bot.src.utils.gen_utils.phase import ChatGPT
async def handle(chat, lang, update, context, _message=None):
    from bot.src.handlers import semaphore as tasks
    from bot.src.utils.proxies import (db,interaction_cache,config,datetime,telegram,ParseMode,ChatAction)
    type = update.callback_query.message if update.callback_query else update.message
    if _message: prompt = _message
    else:
        if not context.args:
            await update.effective_chat.send_message(f'{config.lang["mensajes"]["genimagen_noargs"][lang]}', parse_mode=ParseMode.HTML)
            await tasks.releasemaphore(chat=chat)
            return
        else: prompt = ' '.join(context.args)
    if prompt == None:
        await update.effective_chat.send_message(f'{config.lang["mensajes"]["genimagen_notext"][lang]}', parse_mode=ParseMode.HTML)
        await tasks.releasemaphore(chat=chat)
        return
    try:
        await tasks.releasemaphore(chat=chat)
        await update.effective_chat.send_action(ChatAction.TYPING)
        insta=ChatGPT(chat, lang)
        resultados = await insta.busqueduck(prompt)
        resultadosbot="""Explain the search results to the user, giving extra information only more than the actual. everything in the language: {language}:\n\n{resultados}\n\nExplain the previous search results to the user, giving extra information only more than the actual. everything in the next language: {language}."""
        await type.chat.send_action(ChatAction.TYPING)
        from bot.src.utils.misc import send_large_message
        await send_large_message(resultados, update)
        #await update.effective_chat.send_message(f'{resultados}', reply_to_message_id=update.effective_message.message_id, parse_mode=ParseMode.MARKDOWN)
        from bot.src.handlers import message
        await message.handle(chat, lang, update, context, _message=resultadosbot.format(resultados=f'{resultados}', language=f'{config.lang["info"]["name"][lang]}'))
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except telegram.error.BadRequest as e:
        text = f'{config.lang["errores"]["genimagen_badrequest"][lang]}'
        await update.effective_chat.send_message(text, parse_mode=ParseMode.HTML)
        await tasks.releasemaphore(chat=chat)
        return
    finally:
        await tasks.releasemaphore(chat=chat)
async def wrapper(update: Update, context: CallbackContext, _message=None, chat=None, lang=None):
    from bot.src.handlers import semaphore as tasks
    from bot.src.utils.proxies import (debe_continuar,obtener_contextos as oc,bb)
    chat, lang = await oc(update)
    if not await debe_continuar(chat, lang, update, context, bypassMention=True): return
    task = bb(handle(chat, lang, update, context, _message))
    await tasks.releasemaphore(chat=chat)
    await tasks.handle(chat, lang, task, update)
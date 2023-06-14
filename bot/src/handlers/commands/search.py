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
        formatted_results_backend, formatted_results_string = await insta.busqueduck(prompt.replace("-", " "))
        await type.chat.send_action(ChatAction.TYPING)
        from bot.src.utils.misc import clean_text, update_dialog_messages, send_large_message
        formatted_results_backend = await clean_text(doc=formatted_results_backend, chat=chat)
        resultadosbot="""{resultados}\n\n parameters[Now you have access to the Internet thanks to the previous searches,you will talk deeply about the search results in general,do not repeat the same search results text and structure,do not write urls,you need to write in the language: {language}]"""
        new_dialog_message = {"search": resultadosbot.format(resultados=f'{formatted_results_backend}', language=f'{config.lang["info"]["name"][lang]}'), "placeholder": ".", "date": datetime.now()}
        await update_dialog_messages(chat, new_dialog_message)
        await send_large_message(formatted_results_string, update)
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
    from bot.src.utils.proxies import (debe_continuar,obtener_contextos as oc, parametros, bb)
    chat, lang = await oc(update)
    await parametros(chat, lang, update)
    if not await debe_continuar(chat, lang, update, context, bypassMention=True): return
    task = bb(handle(chat, lang, update, context, _message))
    await tasks.releasemaphore(chat=chat)
    await tasks.handle(chat, lang, task, update)
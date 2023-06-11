from bot.src.start import Update, CallbackContext
from telegram import InputMediaDocument, InputMediaPhoto
from bot.src.utils.gen_utils.phase import ChatGPT
async def handle(chat, lang, update, context, _message=None):
    from bot.src.handlers import semaphore as tasks
    from bot.src.utils.proxies import (logger,db,interaction_cache,config,datetime,telegram,ParseMode,ChatAction)
    type = update.callback_query.message if update.callback_query else update.message
    if _message:
        prompt = _message
    else:
        if not context.args:
            await type.reply_text(f'{config.lang["mensajes"]["genimagen_noargs"][lang]}', parse_mode=ParseMode.HTML)
            await tasks.releasemaphore(chat=chat)
            return
        else:
            prompt = ' '.join(context.args)
    if prompt == None:
        await type.reply_text(f'{config.lang["mensajes"]["genimagen_notext"][lang]}', parse_mode=ParseMode.HTML)
        await tasks.releasemaphore(chat=chat)
        return
    import openai
    try:
        await tasks.releasemaphore(chat=chat)
        await type.chat.send_action(ChatAction.UPLOAD_PHOTO)
        insta=ChatGPT(chat)
        image_urls = await insta.imagen(prompt)
    except (openai.error.APIError, openai.error.InvalidRequestError) as e:
        if "Request has inappropriate content!" in str(e) or "Your request was rejected as a result of our safety system." in str(e):
            text = f'{config.lang["errores"]["genimagen_rejected"][lang]}'
        else:
            text = f'{config.lang["errores"]["genimagen_other"][lang]}'
        await type.reply_text(text, parse_mode=ParseMode.HTML)
        await tasks.releasemaphore(chat=chat)
        return
    except telegram.error.BadRequest as e:
        text = f'{config.lang["errores"]["genimagen_badrequest"][lang]}'
        await type.reply_text(text, parse_mode=ParseMode.HTML)
        await tasks.releasemaphore(chat=chat)
        return
    except Exception as e:
        if "Response payload is not completed" in str(e):
            print("PayloadError ImageGen")
    try:
        image_group=[]
        document_group=[]
        await type.chat.send_action(ChatAction.UPLOAD_PHOTO)
        for i, image_url in enumerate(image_urls):
            image = InputMediaPhoto(image_url)
            image_group.append(image)
            document = InputMediaDocument(image_url, parse_mode=ParseMode.HTML, filename=f"imagen_{i}.png")
            document_group.append(document)
        await context.bot.send_media_group(chat_id=update.effective_message.chat.id, media=image_group, reply_to_message_id=update.effective_message.message_id)
        await context.bot.send_media_group(chat_id=update.effective_message.chat.id, media=document_group, reply_to_message_id=update.effective_message.message_id)
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except Exception as e:
        if "referenced before assignment" in str(e):
            await type.reply_text(f'{config.lang["errores"]["genimagen_badrequest"][lang]}', parse_mode=ParseMode.HTML)
            return
        else:
            logger.error(e)
            return
    finally:
        await tasks.releasemaphore(chat=chat)
async def wrapper(update: Update, context: CallbackContext, _message=None, chat=None, lang=None):
    from bot.src.handlers import semaphore as tasks
    from bot.src.utils.proxies import (debe_continuar,obtener_contextos as oc,bb)
    chat, lang = await oc(update)
    if not await debe_continuar(chat, lang, update, context): return
    task = bb(handle(chat, lang, update, context, _message))
    await tasks.releasemaphore(chat=chat)
    await tasks.handle(chat, lang, task, update)
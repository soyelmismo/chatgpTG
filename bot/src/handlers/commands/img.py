from bot.src.start import Update, CallbackContext
from telegram import InputMediaDocument, InputMediaPhoto
from bot.src.utils.gen_utils.phase import ChatGPT
import asyncio
from bot.src.utils import config
from bot.src.utils.proxies import logger, db, interaction_cache, config, datetime, telegram, ParseMode, ChatAction

document_groups = {}  # Almacena todos los document_groups con su message_id
async def remove_document_group(message_id, borrar=None, update=None, lang=None):
    if not borrar:
        await asyncio.sleep(config.generatedimagexpiration * 60)  # Espera (# * 60 segundos)
    if f'{message_id}' in document_groups:
        del document_groups[f'{message_id}']
        if update:
            await update.effective_chat.send_message(text=f'{config.lang["mensajes"]["fotos_borradas_listo"][lang]}', reply_to_message_id=message_id)
async def create_document_group(update, context, lang, image_group, document_group, mensaje_group_id):
    document_groups[f'{mensaje_group_id}'] = document_group
    asyncio.create_task(remove_document_group(f'{mensaje_group_id}'))
    keyboard = []
    keyboard.append([])
    keyboard[0].append({"text": "🗑", "callback_data": f"imgdownload|{mensaje_group_id}|borrar"})
    keyboard[0].append({"text": "💾", "callback_data": f"imgdownload|{mensaje_group_id}|recibir"})
    await context.bot.send_media_group(chat_id=update.effective_message.chat.id, media=image_group, reply_to_message_id=mensaje_group_id)
    await update.effective_chat.send_message(text=f'{config.lang["mensajes"]["preguntar_descargar_fotos"][lang].format(expirationtime=config.generatedimagexpiration)}', reply_to_message_id=mensaje_group_id, reply_markup={"inline_keyboard": keyboard})

async def get_prompt(context, chattype, _message, lang):
    if _message:
        return _message
    if not context.args:
        await chattype.reply_text(f'{config.lang["mensajes"]["genimagen_noargs"][lang]}', parse_mode=ParseMode.HTML)
        return None
    prompt = ' '.join(context.args)
    if not prompt:
        await chattype.reply_text(f'{config.lang["mensajes"]["genimagen_notext"][lang]}', parse_mode=ParseMode.HTML)
        return None
    return prompt

async def get_image_urls(chattype, chat, prompt, lang):
    import openai
    try:
        await chattype.chat.send_action(ChatAction.UPLOAD_PHOTO)
        insta = ChatGPT(chat)
        return await insta.imagen(prompt)
    except (openai.error.APIError, openai.error.InvalidRequestError) as e:
        await handle_openai_errors(e, chattype, lang)
    except telegram.error.BadRequest as e:
        await chattype.reply_text(f'{config.lang["errores"]["genimagen_badrequest"][lang]}', parse_mode=ParseMode.HTML)
    except Exception as e:
        if "Response payload is not completed" in str(e):
            logger.error("PayloadError ImageGen")
    return None

async def handle_openai_errors(e, chattype, lang):
    if "Request has inappropriate content!" in str(e) or "Your request was rejected as a result of our safety system." in str(e):
        text = f'{config.lang["errores"]["genimagen_rejected"][lang]}'
    else:
        text = f'{config.lang["errores"]["genimagen_other"][lang]}'
    await chattype.reply_text(text, parse_mode=ParseMode.HTML)

async def send_image_group(update, context, lang, chat, image_urls, chattype):
    try:
        image_group = []
        document_group = []
        await chattype.chat.send_action(ChatAction.UPLOAD_PHOTO)
        for i, image_url in enumerate(image_urls):
            image = InputMediaPhoto(image_url)
            image_group.append(image)
            document = InputMediaDocument(image_url, parse_mode=ParseMode.HTML, filename=f"imagen_{i}.png")
            document_group.append(document)
        mensaje_group_id = update.effective_message.message_id
        await create_document_group(update, context, lang, image_group, document_group, mensaje_group_id)
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except Exception as e:
        if "referenced before assignment" in str(e):
            await chattype.reply_text(f'{config.lang["errores"]["genimagen_badrequest"][lang]}', parse_mode=ParseMode.HTML)
        else:
            logger.error(e)

async def wrapper(update: Update, context: CallbackContext, _message=None):
    from bot.src.handlers import semaphore as tasks
    from bot.src.utils.proxies import (debe_continuar,obtener_contextos as oc,bb)
    chat, lang = await oc(update)
    if not await debe_continuar(chat, lang, update, context, bypassmention=True): return
    task = bb(handle(chat, lang, update, context, _message))
    await tasks.releasemaphore(chat=chat)
    await tasks.handle(chat, lang, task, update)
    
async def handle(chat, lang, update, context, _message=None):
    from bot.src.handlers import semaphore as tasks
    chattype = update.callback_query.message if update.callback_query else update.message
    prompt = await get_prompt(context, chattype, _message, lang)
    if not prompt:
        return
    image_urls = await get_image_urls(chattype, chat, prompt, lang)
    if not image_urls:
        return
    await send_image_group(update, context, lang, chat, image_urls, chattype)
    await tasks.releasemaphore(chat=chat)

async def callback(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import obtener_contextos as oc, config
    query = update.callback_query
    _, lang = await oc(update)
    await query.answer()
    action = query.data.split("|")[2]
    msgid = query.data.split("|")[1]
    if action == "recibir":
        documentos=document_groups.get(f'{msgid}')
        if not documentos:
            await update.effective_chat.send_message(text=f'{config.lang["mensajes"]["fotos_ya_expiraron"][lang]}', reply_to_message_id=update.effective_message.message_id)
        else:
            await context.bot.send_media_group(chat_id=update.effective_message.chat.id, media=documentos, reply_to_message_id=msgid)
            await remove_document_group(message_id=msgid, borrar=True)
            await query.message.delete()
    elif action == "borrar":
        await remove_document_group(message_id=msgid, borrar=True, update=update, lang=lang)
        await query.message.delete()
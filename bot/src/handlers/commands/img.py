from bot.src.start import Update, CallbackContext
from telegram import InputMediaDocument, InputMediaPhoto
from bot.src.utils.gen_utils.phase import ChatGPT
import asyncio
from bot.src.utils import config
from bot.src.utils.proxies import debe_continuar, obtener_contextos as oc, bb, logger, db, interaction_cache, config, datetime, telegram, ParseMode, ChatAction, parametros
from bot.src.handlers import semaphore as tasks

document_groups = {}  # Almacena todos los document_groups con su message_id
async def remove_document_group(message_id, borrar=None, update=None, lang=None):
    if not borrar:
        await asyncio.sleep(config.generatedimagexpiration * 60)  # Espera (# * 60 segundos)
    if f'{message_id}' in document_groups:
        del document_groups[f'{message_id}']
        if lang:
            await update.effective_chat.send_message(text=f'{config.lang["mensajes"]["fotos_borradas_listo"][lang]}', reply_to_message_id=message_id)

async def create_document_group(update, context, lang, image_group, document_group, mensaje_group_id, seed=None, chattype=None):
    try:
        await chattype.chat.send_action(ChatAction.UPLOAD_PHOTO)
        document_groups[f'{mensaje_group_id}'] = document_group
        asyncio.create_task(remove_document_group(message_id=f'{mensaje_group_id}', update=update))
        keyboard = []
        keyboard.append([])
        keyboard[0].append({"text": "🗑", "callback_data": f"imgdownload|{mensaje_group_id}|borrar"})
        keyboard[0].append({"text": "💾", "callback_data": f"imgdownload|{mensaje_group_id}|recibir"})
        retiv = config.lang["mensajes"]["preguntar_descargar_fotos"][lang].format(expirationtime=config.generatedimagexpiration)
        if seed:
            text=f'`{seed}`\n\n{retiv}'
        else:
            text=f'{retiv}'
        try:
            await send_media_group_with_retry(update, text, context, update.effective_message.chat.id, image_group, keyboard, reply_to_message_id=mensaje_group_id)
        except telegram.error.BadRequest as e:
            if "Replied message not found" in str(e):
                await send_media_group_with_retry(update, text, context, update.effective_message.chat.id, image_group, keyboard)
            else:
                raise ValueError(f"telegram BadRequest > {e}")
    except Exception as e:
        await handle_errors(f'create_document_group > {e}', None, lang, chattype)

async def send_media_group_with_retry(update, text, context, chat_id, media_group, keyboard, reply_to_message_id=None, mensaje_group_id=None):
    try:
        await context.bot.send_media_group(chat_id=chat_id, media=media_group, reply_to_message_id=reply_to_message_id)
        if text:
            await update.effective_chat.send_message(text, parse_mode=ParseMode.MARKDOWN, reply_to_message_id=mensaje_group_id, reply_markup={"inline_keyboard": keyboard})
    except telegram.error.BadRequest as e:
        if "Replied message not found" in str(e):
            await context.bot.send_media_group(chat_id=update.effective_message.chat.id, media=media_group)
            if text:
                await update.effective_chat.send_message(text, parse_mode=ParseMode.MARKDOWN, reply_markup={"inline_keyboard": keyboard})
        else:
            raise RuntimeError(f'send_media_group_with_retry > {e}')

async def get_prompt(update: Update, context: CallbackContext, chattype, _message, chat, lang):
    try:
        if _message:
            return _message
        if not context.args:
            await tasks.releasemaphore(chat=chat)
            await options_handle(update, context)
            return

        first_arg = context.args[0]
        seed = None

        if first_arg.startswith("seed:"):
            import hashlib
            seed = first_arg[5:]
            prompt = ' '.join(context.args[1:])
            if not seed.isdigit():
                seed = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
            else:
                seed = int(seed)
            seed = abs(seed)
            seed %= 10**16
        else:
            prompt = ' '.join(context.args)  # El primer argumento se incluye en el prompt

        if not prompt:
            await chattype.reply_text(f'{config.lang["mensajes"]["genimagen_notext"][lang]}', parse_mode=ParseMode.HTML)
            return None

        return prompt, seed
    except Exception as e:
        await handle_errors(f'get_prompt > {e}', chattype, lang, chat)

async def get_image_urls(chattype, chat, lang, update, prompt, seed=None):
    try:
        style=None
        ratio=None
        _, _, _, current_api, style, ratio = await parametros(chat, lang, update)
        insta = ChatGPT(chat)
        for attempt in range(1, (config.max_retries) + 1):
            try:
                await chattype.chat.send_action(ChatAction.UPLOAD_PHOTO)
                image_urls, seed = await asyncio.wait_for(insta.imagen(prompt, current_api, style, ratio, seed), timeout=20)
                if not image_urls: raise FileNotFoundError("No se obtuvieron imagenes.")
                if not seed: raise ValueError("No se obtuvo la semilla.")
                return image_urls, current_api, seed
            except Exception as e:
                if isinstance(e, asyncio.TimeoutError): None
                if attempt < config.max_retries: await asyncio.sleep(0.75)
                else: raise ConnectionError(f"_make_image_call. {e}")
    except telegram.error.BadRequest as e:
        await chattype.reply_text(f'{config.lang["errores"]["genimagen_badrequest"][lang]}', parse_mode=ParseMode.HTML)
    except Exception as e:
        await handle_errors(f'get_image_urls > {e}', chattype, lang, chat)
    return None

async def handle_errors(e, chattype, lang, chat):
    if "Request has inappropriate content!" in str(e) or "Your request was rejected as a result of our safety system." in str(e):
        text = f'{config.lang["errores"]["genimagen_rejected"][lang]}'
    else:
        text = f'{config.lang["errores"]["genimagen_other"][lang]}'
    if chattype:
        await chattype.reply_text(text, parse_mode=ParseMode.HTML)
    await tasks.releasemaphore(chat=chat)
    raise RuntimeError(f"handle_errors > {e}")

async def send_image_group(update, context, lang, chat, image_urls, chattype, current_api, seed=None):
    try:
        image_group = []
        document_group = []
        if current_api == "imaginepy":
            image_urls.seek(0)  # Ensure we're at the start of the file
            image = InputMediaPhoto(image_urls)
            image_group.append(image)
            image_urls.seek(0)
            document = InputMediaDocument(image_urls, parse_mode=ParseMode.HTML, filename=f"imagen.png")
            document_group.append(document)
        else:
            for i, image_url in enumerate(image_urls):
                image = InputMediaPhoto(image_url)
                image_group.append(image)
                document = InputMediaDocument(image_url, parse_mode=ParseMode.HTML, filename=f"imagen_{i}.png")
                document_group.append(document)
    except Exception as e:
        if "referenced before assignment" in str(e):
            await chattype.reply_text(f'{config.lang["errores"]["genimagen_badrequest"][lang]}', parse_mode=ParseMode.HTML)
        else:
            await handle_errors(f'send_image_group > {e}', chattype, lang, chat)
    finally:
        mensaje_group_id = update.effective_message.message_id
        await create_document_group(update, context, lang, image_group, document_group, mensaje_group_id, seed, chattype)
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())

async def wrapper(update: Update, context: CallbackContext, _message=None):
    chat, lang = await oc(update)
    if not await debe_continuar(chat, lang, update, context, bypassmention=True): return
    task = bb(handle(chat, lang, update, context, _message))
    await tasks.releasemaphore(chat=chat)
    await tasks.handle(chat, lang, task, update)

async def handle(chat, lang, update, context, _message=None):
    try:
        from bot.src.handlers import semaphore as tasks
        chattype = update.callback_query.message if update.callback_query else update.message
        prompt, seed = await get_prompt(update, context, chattype, _message, chat, lang)
        image_urls, current_api, seed = await get_image_urls(chattype, chat, lang, update, prompt, seed)
    except Exception as e:
        logger.error(e)
        await tasks.releasemaphore(chat=chat)
        raise RuntimeError(f'image_handle > {e}')
    finally:
        await send_image_group(update, context, lang, chat, image_urls, chattype, current_api, seed)
        await tasks.releasemaphore(chat=chat)

#callback de recibir o borrar imagenes
async def callback(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import obtener_contextos as oc, config
    query = update.callback_query
    _, lang = await oc(update)
    await query.answer()
    action = query.data.split("|")[2]
    msgid = query.data.split("|")[1]
    if action == "recibir":
        documentos = document_groups.get(f'{msgid}')
        if not documentos:
            await update.effective_chat.send_message(text=f'{config.lang["mensajes"]["fotos_ya_expiraron"][lang]}', reply_to_message_id=update.effective_message.message_id)
            await query.message.delete()
        else:
            try:
                await send_media_group_with_retry(update, None, context, update.effective_message.chat.id, documentos, keyboard=None, reply_to_message_id=msgid)
                await remove_document_group(message_id=msgid, borrar=True)
                await query.message.delete()
            except telegram.error.BadRequest as e:
                if "Replied message not found" in str(e):
                    await send_media_group_with_retry(update, None, context, update.effective_message.chat.id, documentos, keyboard=None)
                else:
                    raise ValueError(f"telegram BadRequest > {e}")
    elif action == "borrar":
        await remove_document_group(message_id=msgid, borrar=True, update=update, lang=lang)
        await query.message.delete()


import bot.src.handlers.menu as menu
async def options_handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,logger,config,ParseMode)
    try:
        chat, _ = await oc(update)
        text, reply_markup = await menu.get(menu_type="image_api", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f'<image_api_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]} {e}')

async def options_callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await menu.handle(update)
    await menu.refresh(query, update, context, page_index, menu_type="image_api")

async def options_set(update: Update, context: CallbackContext):
    from bot.src.utils.constants import constant_db_image_api
    from bot.src.utils.proxies import image_api_cache
    chat, _ = await oc(update)
    query, _, seleccion, page_index, _ = await menu.handle(update)
    menu_type="image_api"
    if seleccion == "imaginepy":
        menu_type="imaginepy"
    if seleccion in config.api["available_image_api"] and (image_api_cache.get(chat.id) is None or image_api_cache.get(chat.id)[0] != seleccion):
        image_api_cache[chat.id] = (seleccion, datetime.now())
        await db.set_chat_attribute(chat, f'{constant_db_image_api}', seleccion)
    await menu.refresh(query, update, context, page_index, menu_type=menu_type, chat=chat)
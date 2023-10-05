from bot.src.tasks.apis_image import img_vivas
from datetime import datetime
from bot.src.start import Update, CallbackContext
from telegram import InputMediaDocument, InputMediaPhoto
from bot.src.utils.gen_utils.phase import ChatGPT
import asyncio
from bot.src.utils import config
from bot.src.utils.proxies import debe_continuar, obtener_contextos as oc, bb, db, interaction_cache, config, telegram, ParseMode, ChatAction, parametros, menusnotready, errorpredlang
from bot.src.handlers import semaphore as tasks
from bot.src.handlers.error import mini_handle as handle_errors
from bot.src.utils.constants import logger, Style
#algunos mensajes de error
rmnf = "Replied message not found"

document_groups = {}  # Almacena todos los document_groups con su message_id
async def remove_document_group(message_id, borrar=None, update=None, lang=None):
    if not borrar:
        await asyncio.sleep(config.generatedimagexpiration * 60)  # Espera (# * 60 segundos)
    if f'{message_id}' in document_groups:
        del document_groups[f'{message_id}']
        if lang:
            msg = await update.effective_chat.send_message(text=f'{config.lang[lang]["mensajes"]["fotos_borradas_listo"]}')
            await asyncio.sleep(3)
            await msg.delete()

async def create_document_group(update, context, lang, image_group, document_group, mensaje_group_id, chattype=None, caption=None):
    try:
        await chattype.chat.send_action(ChatAction.UPLOAD_PHOTO)
        document_groups[f'{mensaje_group_id}'] = document_group
        asyncio.create_task(remove_document_group(message_id=f'{mensaje_group_id}', update=update))
        keyboard = []
        keyboard.append([])
        keyboard[0].append({"text": "🗑", "callback_data": f"imgdownload|{mensaje_group_id}|borrar"})
        keyboard[0].append({"text": "💾", "callback_data": f"imgdownload|{mensaje_group_id}|recibir"})
        text = config.lang[lang]["mensajes"]["preguntar_descargar_fotos"].format(expirationtime=config.generatedimagexpiration)
        try:
            await send_media_group_with_retry(update, text, context, update.effective_message.chat.id, image_group, keyboard, reply_to_message_id=mensaje_group_id, caption=caption, lang=lang)
        except telegram.error.BadRequest as e:
            if rmnf in str(e):
                await send_media_group_with_retry(update, text, context, update.effective_message.chat.id, image_group, keyboard, caption=caption, lang=lang)
            else:
                raise ValueError(f"telegram BadRequest > {e}")
    except Exception as e:
        raise LookupError(f'create_document_group > {e}')

async def send_media_group_with_retry(update: Update, text, context: CallbackContext, chat_id, media_group, keyboard, reply_to_message_id=None, caption=None, lang=None):
    try:
        media_msg = await context.bot.send_media_group(chat_id=chat_id, media=media_group, caption=caption, parse_mode=ParseMode.HTML, reply_to_message_id=reply_to_message_id)
        if not media_msg:
            await expiracion(update, lang)
        if text:
            await update.effective_chat.send_message(text, parse_mode=ParseMode.HTML, reply_to_message_id=media_msg[0].message_id, reply_markup={"inline_keyboard": keyboard})
    except telegram.error.BadRequest as e:
        if rmnf in str(e):
            media_msg = await context.bot.send_media_group(chat_id=update.effective_message.chat.id, media=media_group, caption=caption, parse_mode=ParseMode.MARKDOWN_V2)
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
            return None, None, ''

        first_arg = context.args[0]
        seed = None
        avoid = None
        prompt = ' '.join(context.args)
        if first_arg.startswith('seed:'):
            from hashlib import sha256
            seed = first_arg[5:]
            prompt = ' '.join(context.args[1:])
            if not seed.isdigit():
                seed = int(sha256(seed.encode()).hexdigest(), 16)
            else:
                seed = int(seed)
            seed = abs(seed)
            seed %= 10**10
            seed = str(seed)
        if 'avoid:' in prompt:
            prompt_parts = prompt.split('avoid:')
            prompt = prompt_parts[0].strip()
            avoid = prompt_parts[1].strip()
        if not prompt:
            await chattype.reply_text(f'{config.lang[lang]["mensajes"]["genimagen_notext"]}', parse_mode=ParseMode.HTML)
            return None, None, None
        return prompt, seed, avoid
    except Exception as e:
        raise ValueError(f'get_prompt > {e}')

async def get_image_urls(chattype, chat, lang, update, prompt, seed=None, negative=None):
    try:
        style = None
        ratio = None
        model = None
        _, _, _, current_api, style, ratio, model = await parametros(chat, lang, update)

        insta = await ChatGPT.create(chat)
        for attempt in range(1, (config.max_retries) + 1):
            try:
                await chattype.chat.send_action(ChatAction.UPLOAD_PHOTO)
                #message = await update.effective_chat.send_message(text=f'{config.lang[lang]["mensajes"]["fotos_ya_expiraron"]}', reply_to_message_id=update.effective_message.message_id)
                timeout = 60
                if current_api == "stablehorde":
                    timeout = timeout * 25
                image_urls, seed, model = await asyncio.wait_for(insta.imagen(prompt, model, current_api, style, ratio, seed, negative), timeout=timeout)
                return image_urls, current_api, seed, style, ratio, model
            except Exception as e:
                if isinstance(e, asyncio.TimeoutError): None
                elif attempt < config.max_retries: await asyncio.sleep(0.75)
                else: raise RuntimeError(f"GenerationError: {e}")
    except telegram.error.BadRequest as e:
        await chattype.reply_text(f'{config.lang[lang]["errores"]["genimagen_badrequest"]}', parse_mode=ParseMode.HTML)
    except Exception as e:
        raise TypeError(f'get_image_urls > {e}')

async def send_image_group(update, context, lang, chat, image_urls, chattype, current_api, prompt=None, seed=None, negative=None, style=None, ratio=None, model=None):
    try:
        image_group = []
        document_group = []
        
        caption = f'✏️ "<strong><code>{prompt}</code></strong>"'
        if current_api == "stablehorde":
            if negative != None:
                caption += f'\n❌ "<code>{negative}</code>"'
            caption += f'\n\n🌱 <code>{seed}</code>\n🧠 <strong>{model}</strong>\n'
        if not seed:
            caption += '\n\n'
        caption += f'🧵 <strong>{config.api["info"][current_api]["name"]}</strong>\n🎨 <strong>{Style[style].value[1]}</strong>'
        for i, image_url in enumerate(image_urls):
            if current_api == "stablehorde":
                image_url.seek(0)  # Ensure we're at the start of the file
                image = InputMediaPhoto(image_url)
                image_group.append(image)
                image_url.seek(0)
                document = InputMediaDocument(image_url, filename=image_url.name)
                document_group.append(document)
            else:
                image = InputMediaPhoto(image_url)
                image_group.append(image)
                document = InputMediaDocument(image_url, filename=f"imagen_{i}.png")
                document_group.append(document)
        mensaje_group_id = update.effective_message.message_id
        await create_document_group(update, context, lang, image_group, document_group, mensaje_group_id, chattype, caption)
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except Exception as e:
        if "referenced before assignment" in str(e):
            await chattype.reply_text(f'{config.lang[lang]["errores"]["genimagen_badrequest"]}', parse_mode=ParseMode.HTML)
        else:
            raise LookupError(f'send_image_group > {e}')

async def wrapper(update: Update, context: CallbackContext, _message=None):
    chat, lang = await oc(update)
    if not await debe_continuar(chat, lang, update, context, bypassmention=True): return
    task = bb(handle(chat, lang, update, context, _message))
    await tasks.releasemaphore(chat=chat)
    await tasks.handle(chat, task)

async def handle(chat, lang, update, context, _message=None):
    try:
        from bot.src.handlers import semaphore as tasks
        chattype = update.callback_query.message if update.callback_query else update.message
        prompt, seed, negative = await get_prompt(update, context, chattype, _message, chat, lang)
        if prompt != None:
            image_urls, current_api, seed, style, ratio, model = await get_image_urls(chattype, chat, lang, update, prompt, seed, negative)
            if image_urls is None: raise FileNotFoundError("No se obtuvieron imagenes.")
            await send_image_group(update, context, lang, chat, image_urls, chattype, current_api, prompt, seed, negative, style, ratio, model)
    except Exception as e:
        await handle_errors(f'image_handle > {e}', lang, chat, update)
    finally:
        await tasks.releasemaphore(chat=chat)

#callback de recibir o borrar imagenes
pendientes = {}
async def callback(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import obtener_contextos as oc, config
    query = update.callback_query
    _, lang = await oc(update)
    await query.answer()
    action = query.data.split("|")[2]
    msgid = query.data.split("|")[1]
    if action == "recibir":
        await callback_recibir(update, context, msgid, lang)
    elif action == "borrar":
        asyncio.create_task(remove_document_group(message_id=msgid, borrar=True, update=update, lang=lang))
    await query.message.delete()

async def expiracion(update, lang, msgid=None):
    replid = None
    if update.effective_message.message_id:
        replid = update.effective_message.message_id
    elif msgid:
        replid = msgid
    if replid:
        await update.effective_chat.send_message(text=f'{config.lang[lang]["mensajes"]["fotos_ya_expiraron"]}', reply_to_message_id=replid)

async def callback_recibir(update, context, msgid, lang):
    documentos = document_groups.get(f'{msgid}')
    if not documentos:
        await expiracion(update, lang, msgid)
    else:
        try:
            if not pendientes.get(msgid):
                pendientes[msgid] = True
                await send_media_group_with_retry(update, None, context, update.effective_message.chat.id, documentos, keyboard=None, reply_to_message_id=msgid, lang=lang)
                await remove_document_group(message_id=msgid, borrar=True)
                pendientes.pop(msgid)
        except telegram.error.BadRequest as e:
            if rmnf in str(e):
                await send_media_group_with_retry(update, None, context, update.effective_message.chat.id, documentos, keyboard=None, lang=lang)
            else:
                raise ValueError(f"telegram BadRequest > {e}")


from bot.src.handlers.menu import handle as hh, get as gg, refresh as rr
async def options_handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,ParseMode)
    try:
        chat, _ = await oc(update)
        text, reply_markup = await gg(menu_type="image_api", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception as e: logger.error(f'{__name__}: <image_api_handle> {errorpredlang}: {menusnotready} {e}')

async def options_callback(update: Update, context: CallbackContext):
    query, _, _, page_index, _ = await hh(update)
    await rr(query, update, context, page_index, menu_type="image_api")

async def options_set(update: Update, context: CallbackContext):
    from bot.src.utils.constants import constant_db_image_api, constant_db_image_api_styles
    from bot.src.utils.proxies import image_api_cache, image_api_styles_cache
    chat, _ = await oc(update)
    query, propsmenu, seleccion, page_index, _ = await hh(update)
    menu_type="image_api"
    if seleccion == "stablehorde":
        menu_type="stablehorde"
    elif seleccion != "image_api":
        menu_type="image_api_styles"
    if seleccion in img_vivas and (image_api_cache.get(chat.id) is None or image_api_cache.get(chat.id)[0] != seleccion):
        image_api_cache[chat.id] = (seleccion, datetime.now())
        await db.set_chat_attribute(chat, f'{constant_db_image_api}', seleccion)
    elif propsmenu == "set_image_api_styles":
        menu_type = "image_api_styles"
        if seleccion != "paginillas":
            image_api_styles_cache[chat.id] = (seleccion, datetime.now())
            await db.set_chat_attribute(chat, f'{constant_db_image_api_styles}', seleccion)
    await rr(query, update, context, page_index, menu_type=menu_type, chat=chat)

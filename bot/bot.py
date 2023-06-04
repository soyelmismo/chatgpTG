import logging
import asyncio
import traceback
import html
import json
import tempfile
from pathlib import Path
from datetime import datetime
import telegram
from telegram import (
    Update,
    InputMediaDocument,
    InputMediaPhoto,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    AIORateLimiter,
    filters
)
from telegram.constants import ParseMode, ChatAction
import config
import database
import openai_utils
import random
import re

db = database.Database()
logger = logging.getLogger(__name__)
bb = asyncio.create_task
bcs = asyncio.ensure_future
loop = asyncio.get_event_loop()
sleep = asyncio.sleep
chat_locks = {}
chat_tasks = {}

#cache testing
cache_index = ["lang_cache", "chat_mode_cache", "api_cache", "model_cache", "menu_cache", "interaction_cache"]
lang_cache = {}  
chat_mode_cache = {}
api_cache = {}
model_cache = {}
menu_cache = {}
interaction_cache = {}

apis_vivas = []
msg_no_mod = "Message is not modified"


async def obtener_vivas():
    from apistatus import estadosapi
    global apis_vivas
    apis_vivas = await estadosapi()

async def revisar_cache(cache):
    if isinstance(cache, dict):
        for key, value in list(cache.items()):
            if datetime.now() > value[1]:
                del cache[key]

async def handle_chat_task(chat, lang, task, update):
    async with chat_locks[chat.id]:
        chat_tasks[chat.id] = task
        try:
            await acquiresemaphore(chat=chat)
            await task
        except asyncio.CancelledError:
            await update.effective_chat.send_message(f'{config.lang["mensajes"]["cancelado"][lang]}', parse_mode=ParseMode.HTML)
        except RuntimeError as e:
            if 'Event loop is closed' in str(e):
                logger.error("Error: el bucle de eventos ya finalizó")
        finally:
            await releasemaphore(chat=chat)
            if chat.id in chat_tasks:
                del chat_tasks[chat.id]
async def acquiresemaphore(chat):
    lock = chat_locks.get(chat.id)
    if lock is None:
        lock = asyncio.Lock()  # Inicializa un nuevo bloqueo si no existe
        chat_locks[chat.id] = lock
    await lock.acquire()
async def releasemaphore(chat):
    lock = chat_locks.get(chat.id)
    while lock and lock.locked():
        lock.release()

async def is_previous_message_not_answered_yet(chat, lang, update: Update, mensaje_actions=None):
    semaphore = chat_locks.get(chat.id)
    if semaphore and semaphore.locked():
        text = f'{config.lang["mensajes"]["mensaje_semaforo"][lang]}'
        if update.callback_query:
            await update.effective_chat.send_message(text, reply_to_message_id=update.callback_query.message.message_id, parse_mode=ParseMode.HTML)
        else:
            await update.effective_chat.send_message(text, reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML)
        return True
    else:
        return False

async def is_bot_mentioned(update: Update, context: CallbackContext):
    message=update.message
    try:
        if message.chat.type == "private":
            return True

        if message.text is not None and ("@" + context.bot.username) in message.text:
            return True
        
        if message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
            return True
    except:
        return True
    else:
        return False

async def start_handle(update: Update, context: CallbackContext):
    lang = await lang_check(update, context)
    reply_text = f'{config.lang["mensajes"]["mensaje_bienvenido"][lang]}🤖\n\n'
    reply_text += f'{config.lang["mensajes"]["mensaje_ayuda"][lang]}'
    await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)

async def new_dialog_handle(update: Update, context: CallbackContext, chat=None, lang=None):
    try:
        if not chat:
            chat  = await chat_check(update, context)
        if not lang:
            lang = await lang_check(update, context, chat)
        if await is_previous_message_not_answered_yet(chat, lang, update): return
        mododechat_actual, _, _ = await parameters_check(chat, lang, update)
        await db.new_dialog(chat)
        await db.delete_all_dialogs_except_current(chat)
        #Bienvenido!
        await update.effective_chat.send_message(f"{config.chat_mode['info'][mododechat_actual]['welcome_message'][lang]}", parse_mode=ParseMode.HTML)
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except Exception as e:
        logger.error(f'<new_dialog_handle> {config.lang["errores"]["error"][lang]}: {e}')
    finally:
        await releasemaphore(chat=chat)

async def lang_check(update: Update, context: CallbackContext, chat=None):
    if chat is None:
        chat = await chat_check(update, context)
    if chat.id in lang_cache:
        lang = lang_cache[chat.id][0]
    else:
        if await db.chat_exists(chat):
            lang = await db.get_chat_attribute(chat, "current_lang")
        else:
            if update.effective_user.language_code in config.lang["available_lang"]:
                lang = update.effective_user.language_code
            else:
                lang = str(config.pred_lang)
        lang_cache[chat.id] = (lang, datetime.now())
    return lang
async def chat_check(update: Update, context: CallbackContext):
    if update.message:
        chat = update.message.chat
    elif update.callback_query:
        chat = update.callback_query.message.chat
    lang = await lang_check(update, context, chat)
    if not await db.chat_exists(chat):
        await db.add_chat(chat, lang)
        await cambiar_idioma(update, context, chat, lang)
        await db.new_dialog(chat)
    if chat.id not in chat_locks:
        chat_locks[chat.id] = asyncio.Semaphore(1)
    return chat
async def parameters_check(chat, lang, update):
    # Verificar si hay valores inválidos en el usuario
    #chatmode
    if chat.id in chat_mode_cache:  
        mododechat_actual = chat_mode_cache[chat.id][0]
    else:
        mododechat_actual = await db.get_chat_attribute(chat, 'current_chat_mode')
        chat_mode_cache[chat.id] = (mododechat_actual, datetime.now())
    if mododechat_actual not in config.chat_mode["available_chat_mode"]:
        mododechat_actual = config.chat_mode["available_chat_mode"][1]
        chat_mode_cache[chat.id] = (mododechat_actual, datetime.now())
        await db.set_chat_attribute(chat, "current_chat_mode", mododechat_actual)
        await update.effective_chat.send_message(f'{config.lang["errores"]["reset_chat_mode"][lang].format(new=mododechat_actual)}')
    #api
    if chat.id in api_cache:
        api_actual = api_cache[chat.id][0]
    else:
        api_actual = await db.get_chat_attribute(chat, 'current_api')
        api_cache[chat.id] = (api_actual, datetime.now())
    if not apis_vivas:
        raise LookupError(config.lang["errores"]["apis_vivas_not_ready_yet"][config.pred_lang])
    if api_actual not in apis_vivas:
        api_actual = apis_vivas[random.randint(0, len(apis_vivas) - 1)]
        api_cache[chat.id] = (api_actual, datetime.now())
        await db.set_chat_attribute(chat, "current_api", api_actual)
        await update.effective_chat.send_message(f'{config.lang["errores"]["reset_api"][lang].format(new=config.api["info"][api_actual]["name"])}')
    #model
    if chat.id in model_cache:
        modelo_actual = model_cache[chat.id][0]
    else:
        modelo_actual = await db.get_chat_attribute(chat, 'current_model')
        model_cache[chat.id] = (modelo_actual, datetime.now())
    modelos_disponibles=config.api["info"][api_actual]["available_model"]
    if modelo_actual not in modelos_disponibles:
        modelo_actual = modelos_disponibles[random.randint(0, len(modelos_disponibles) - 1)]
        model_cache[chat.id] = (modelo_actual, datetime.now())
        await db.set_chat_attribute(chat, "current_model", modelo_actual)
        await update.effective_chat.send_message(f'{config.lang["errores"]["reset_model"][lang].format(api_actual_name=config.api["info"][api_actual]["name"], new_model_name=config.model["info"][modelo_actual]["name"])}')
    return mododechat_actual, api_actual, modelo_actual

async def cambiar_idioma(update: Update, context: CallbackContext, chat=None, lang=None):
    if not chat:
        chat = await chat_check(update, context)
    if not lang:
        lang = await lang_check(update, context, chat)
    else:
        if lang_cache.get(chat.id)[0] if lang_cache.get(chat.id)[0] is not None else None != lang:
            await db.set_chat_attribute(chat, "current_lang", lang)
            lang_cache[chat.id] = (lang, datetime.now())
            await update.effective_chat.send_message(f'{config.lang["info"]["bienvenida"][lang]}')
    return lang

async def help_handle(update: Update, context: CallbackContext):
    chat = await chat_check(update, context)
    lang = await lang_check(update, context, chat)
    await update.message.reply_text(config.lang["mensajes"]["mensaje_ayuda"][lang], parse_mode=ParseMode.HTML)

async def help_group_chat_handle(update: Update, context: CallbackContext):
    chat = await chat_check(update, context)
    lang = await lang_check(update, context, chat)    
    text = config.lang["mensajes"]["ayuda_grupos"][lang].format(bot_username="@" + context.bot.username)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    await update.message.reply_video(config.help_group_chat_video_path)

async def retry_handle(update: Update, context: CallbackContext, chat=None, lang=None, mensaje_actions=None):
    if not chat:
        chat = await chat_check(update, context)
    if not lang:
        lang = await lang_check(update, context, chat)
    if await is_previous_message_not_answered_yet(chat, lang, update): return
    dialog_messages = await db.get_dialog_messages(chat, dialog_id=None)
    if len(dialog_messages) == 0:
        await releasemaphore(chat=chat)
        text = config.lang["mensajes"]["no_retry_mensaje"][lang]
        if mensaje_actions:
            await mensaje_actions.reply_text(text, reply_to_message_id=mensaje_actions.message_id)
        else:
            await update.message.reply_text(text, reply_to_message_id=update.message.message_id)
        return
    last_dialog_message = dialog_messages.pop()
    await db.set_dialog_messages(chat, dialog_messages, dialog_id=None)  # last message was removed from the context
    interaction_cache[chat.id] = ("visto", datetime.now())
    await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    await releasemaphore(chat=chat)
    _message = last_dialog_message["user"]
    await message_handle(chat, lang, update, context, _message)

async def check_message(update: Update, _message=None):
    raw_msg = _message or update.effective_message
    if not isinstance(raw_msg, str):
        if raw_msg.text:
            _message = raw_msg.text
        else:
            _message = raw_msg.reply_to_message.text
    return raw_msg, _message

async def add_dialog_message(chat, new_dialog_message):
    await db.set_dialog_messages(
        chat,
        await db.get_dialog_messages(chat, dialog_id=None) + [new_dialog_message],
        dialog_id=None
    )

async def message_handle_wrapper(update, context):
    if update.edited_message:
        return
    chat = await chat_check(update, context)
    lang = await lang_check(update, context, chat)
    try:
        # check if bot was mentioned (for groups)
        if not await is_bot_mentioned(update, context): return
        if await is_previous_message_not_answered_yet(chat, lang, update): return
        await parameters_check(chat, lang, update)
        task = bb(message_handle(chat, lang, update, context))
        bcs(handle_chat_task(chat, lang, task, update))
    except Exception as e:
        logger.error(f'<message_handle_wrapper> {config.lang["errores"]["error"][lang]}: {e}')
async def message_handle(chat, lang, update: Update, context: CallbackContext, _message=None):
    if _message:
        raw_msg = await check_message(update, _message)
        raw_msg = raw_msg[0]
    else:
        raw_msg, _message = await check_message(update, _message)
        if chat.type != "private":
            _message = _message.replace("@" + context.bot.username, "").strip()
            _message = f"{raw_msg.from_user.first_name}@{raw_msg.from_user.username}: {_message}"
    try:
        if raw_msg.entities and config.switch_urls == "True":
            urls = await urls_wrapper(raw_msg, chat, lang, update)
            if urls:
                await releasemaphore(chat=chat)
                task = bb(url_handle(chat, lang, update, urls))
                bcs(handle_chat_task(chat, lang, task, update))
                return
    except AttributeError:
        pass
    dialog_messages = await db.get_dialog_messages(chat, dialog_id=None)
    if chat.id in chat_mode_cache:
        chat_mode = chat_mode_cache[chat.id][0]
    else:
        chat_mode = await db.get_chat_attribute(chat, "current_chat_mode")
        chat_mode_cache[chat.id] = (chat_mode, datetime.now())
    if chat.id in interaction_cache:
        last_interaction = interaction_cache[chat.id][1]
    else:
        last_interaction = await db.get_chat_attribute(chat, "last_interaction")
    if (datetime.now() - last_interaction).seconds > config.dialog_timeout and len(dialog_messages) > 0:
        if config.timeout_ask:
            await ask_timeout_handle(chat, lang, update, _message)
            return
        else:
            await new_dialog_handle(update, context, chat, lang)
            await update.effective_chat.send_message(f'{config.lang["mensajes"]["timeout_ask_false"][lang].format(chatmode=config.chat_mode["info"][chat_mode]["name"][lang])}', parse_mode=ParseMode.HTML)
    if chat.id in model_cache:
        current_model = model_cache[chat.id][0]
    else:
        current_model = await db.get_chat_attribute(chat, "current_model")
        model_cache[chat.id] = (current_model, datetime.now())
    await releasemaphore(chat=chat)
    task = bb(message_handle_fn(update, context, _message, chat, lang, dialog_messages, chat_mode, current_model))
    bcs(handle_chat_task(chat, lang, task, update))
    
async def message_handle_fn(update, context, _message, chat, lang, dialog_messages, chat_mode, current_model):
    try:
        if not _message:
            await update.effective_chat.send_message(f'{config.lang["mensajes"]["message_empty_handle"][lang]}', parse_mode=ParseMode.HTML)
            return
        if chat.type != "private":
            upd=250
            timer=0.04
        else:
            upd=50
            timer=0.02
        parse_mode = ParseMode.HTML if config.chat_mode["info"][chat_mode]["parse_mode"] == "html" else ParseMode.MARKDOWN
        keyboard = []
        keyboard.append([])
        keyboard[0].append({"text": "🚫", "callback_data": "actions|cancel"})
        await update.effective_chat.send_action(ChatAction.TYPING)
        placeholder_message = await update.effective_chat.send_message("🤔", reply_markup={"inline_keyboard": keyboard}, parse_mode=parse_mode)
        gen = openai_utils.ChatGPT(chat, lang, model=current_model).send_message(_message, dialog_messages, chat_mode)
        prev_answer = ""
        # Segunda fila de botones con el botón de reintentar
        keyboard[0].append({"text": "🔄", "callback_data": "actions|retry"})
        async for status, gen_answer in gen:
            answer = gen_answer[:4096]  # telegram message limit
            if abs(len(answer) - len(prev_answer)) < upd and status != "finished":  # Comparar con el valor de corte 
                continue
            try:
                await context.bot.edit_message_text(f'{answer}...⏳', chat_id=placeholder_message.chat.id, message_id=placeholder_message.message_id, disable_web_page_preview=True, reply_markup={"inline_keyboard": keyboard}, parse_mode=parse_mode)
            except telegram.error.BadRequest as e:
                if str(e).startswith(msg_no_mod):
                    continue
                #else: #ocasiona errores
                    #await context.bot.edit_message_text(f'{answer}...⏳', chat_id=placeholder_message.chat.id, message_id=placeholder_message.message_id, disable_web_page_preview=True, reply_markup={"inline_keyboard": keyboard})
            await sleep(timer)  # Esperar un poco para evitar el flooding
            prev_answer = answer
        await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat.id, message_id=placeholder_message.message_id, disable_web_page_preview=True, reply_markup={"inline_keyboard": keyboard}, parse_mode=parse_mode)
        # update chat data
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())
        new_dialog_message = {"user": _message, "bot": answer, "date": datetime.now()}
        await add_dialog_message(chat, new_dialog_message)
        await releasemaphore(chat=chat)
    except telegram.error.Forbidden as e:
        logger.error(f"Error: El bot fue expulsado del chat {chat.title}@{chat.id}.")
    except Exception as e:
        logger.error(f'<message_handle_fn> {config.lang["errores"]["error"][lang]}: {e}')
        await releasemaphore(chat=chat)
        keyboard = []
        keyboard.append([])
        keyboard[0].append({"text": "🔄", "callback_data": "actions|retry"})
        await context.bot.edit_message_text(f'{config.lang["errores"]["error_inesperado"][lang]}', chat_id=placeholder_message.chat.id, message_id=placeholder_message.message_id, reply_markup={"inline_keyboard": keyboard}, parse_mode=parse_mode)
        return
    if config.switch_imgs == "True" and chat_mode == "imagen":
        await generate_image_wrapper(update, context, _message=answer, chat=chat, lang=lang)

async def actions_handle(update: Update, context: CallbackContext):
    chat = await chat_check(update, context)
    lang = await lang_check(update, context, chat)
    query = update.callback_query
    await query.answer()
    action = query.data.split("|")[1]
    mensaje_actions = query.message
    if action == "cancel":
        await cancel_handle(update, context, mensaje_actions)
    else:
        await retry_handle(update, context, chat, lang, mensaje_actions)
        
async def send_large_message(text, update):
    if len(text) <= 4096:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    else:
        # Divide el mensaje en partes más pequeñas
        message_parts = [text[i:i+4096] for i in range(0, len(text), 4096)]
        for part in message_parts:
            await update.message.reply_text(part, parse_mode=ParseMode.HTML)

async def clean_text(doc):
    doc = re.sub(r'[\n\r]+', ' ', doc)  # Eliminar saltos de línea
    doc = re.sub(r' {2,}', ' ', doc)  # Eliminar dos o más espacios seguidos
    doc = doc.strip()  # Eliminar espacios en blanco al principio y final del string
    return doc
async def extract_clean_text_from_url(url: str) -> str:
    import httpx
    import html2text
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WebView/3.0 Chrome/91.0.4472.124 Safari/537.36"
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url)
    response.raise_for_status()
    content_length = int(response.headers.get('Content-Length', 0))
    if content_length > config.url_max_size * (1024 * 1024):
        raise ValueError("lenghtexceed")
    html_content = response.text
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_images = True
    text_maker.single_line_break = True
    raw_text = text_maker.handle(html_content)
    doc = await clean_text(raw_text)
    return doc
async def url_handle(chat, lang, update, urls):
    for url in urls:
        await update.effective_chat.send_action(ChatAction.TYPING)
        try:
            doc = await extract_clean_text_from_url(url)
            new_dialog_message = {"url": f'{url}: [{doc}]', "user": ".", "date": datetime.now()}
            await add_dialog_message(chat, new_dialog_message)
            text = f'{config.lang["mensajes"]["url_anotado_ask"][lang]}'
        except ValueError as e:
            if "lenghtexceed" in str(e):
                text = f'{config.lang["errores"]["url_size_limit"][lang]}: {e}.'
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    interaction_cache[chat.id] = ("visto", datetime.now())
    await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    await releasemaphore(chat=chat)
async def urls_wrapper(raw_msg, chat, lang, update):
    urls = []
    for entity in raw_msg.entities:
        if entity.type == 'url':
            url_add = raw_msg.text[entity.offset:entity.offset+entity.length]
            if "http://" in url_add or "https://" in url_add:
                urls.append(raw_msg.text[entity.offset:entity.offset+entity.length])
    return urls

async def document_handle(chat, lang, update, context):
    try:
        document = update.message.document
        file_size_mb = document.file_size / (1024 * 1024)
        if file_size_mb <= config.file_max_size:
            await update.effective_chat.send_action(ChatAction.TYPING)
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_dir = Path(tmp_dir)
                ext = document.file_name.split(".")[-1]
                doc_path = tmp_dir / Path(document.file_name)
                # download
                doc_file = await context.bot.get_file(document.file_id)
                await doc_file.download_to_drive(doc_path)
                if "pdf" in ext:
                    pdf_file = open(doc_path, 'rb')
                    import PyPDF2
                    read_pdf = PyPDF2.PdfReader(pdf_file)
                    doc = ''
                    paginas = len(read_pdf.pages)
                    if paginas > config.pdf_page_lim:
                        paginas = config.pdf_page_lim - 1
                        raise ValueError(config.lang["errores"]["pdf_pages_limit"][lang].format(paginas=paginas, pdf_page_lim=config.pdf_page_lim))
                    for i in range(paginas):
                        text = read_pdf.pages[i].extract_text()
                        text = text.replace(".\n", "|n_parraf|")  
                        paras = text.split("|n_parraf|")
                        parafo_count = 1
                        for para in paras:
                            if len(para) > 3:
                                doc += f'{config.lang["metagen"]["paginas"][lang]}{i+1}_{config.lang["metagen"]["parrafos"][lang]}{parafo_count}: {para}\n\n'      
                                parafo_count += 1
                else:
                    with open(doc_path, 'r') as f:
                        doc = f.read()
                doc = await clean_text(doc)
                new_dialog_message = {"documento": f'{document.file_name}: [{doc}]', "user": ".", "date": datetime.now()}
                await add_dialog_message(chat, new_dialog_message)
                text = f'{config.lang["mensajes"]["document_anotado_ask"][lang]}'
                interaction_cache[chat.id] = ("visto", datetime.now())
                await db.set_chat_attribute(chat, "last_interaction", datetime.now())
        else:
            raise ValueError(config.lang["errores"]["document_size_limit"][lang].replace("{file_size_mb}", f"{file_size_mb:.2f}").replace("{file_max_size}", str(config.file_max_size)))
    except Exception as e:
        text = f'{config.lang["errores"]["error"][lang]}: {e}'
    finally:
        await releasemaphore(chat=chat)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
async def document_wrapper(update, context):
    chat = await chat_check(update, context)
    lang = await lang_check(update, context, chat)
    if not await is_bot_mentioned(update, context): return
    if await is_previous_message_not_answered_yet(chat, lang, update): return
    task = bb(document_handle(chat, lang, update, context))
    bcs(handle_chat_task(chat, lang, task, update))

async def ocr_image(chat, lang, update, context):
    image = update.message.photo[-1]
    from PIL import Image
    import pytesseract
    import cv2
    import numpy as np
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            await update.effective_chat.send_action(ChatAction.TYPING)
            tmp_dir = Path(tmp_dir)
            img_path = tmp_dir / Path("ocrimagen.jpg")
            image_file = await context.bot.get_file(image.file_id)
            await image_file.download_to_drive(img_path)
            imagen = cv2.imread(str(img_path))
            gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            coords = np.column_stack(np.where(binary > 0))
            rect = cv2.minAreaRect(coords)
            angle = rect[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            (h, w) = imagen.shape[:2]
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(imagen, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            doc = pytesseract.image_to_string(rotated, timeout=50, lang='eng+spa+jpn+chi+deu+fra+rus+por+ita+nld', config='--psm 1')
            interaction_cache[chat.id] = ("visto", datetime.now())
            await db.set_chat_attribute(chat, "last_interaction", datetime.now())
            if len(doc) <= 1:
                text = f'{config.lang["errores"]["error"][lang]}: {config.lang["errores"]["ocr_no_extract"][lang]}'
            else:
                doc = await clean_text(doc)
                text = config.lang["mensajes"]["image_ocr_ask"][lang].format(ocresult=doc)
                new_dialog_message = {"user": f'{config.lang["metagen"]["transcripcion_imagen"][lang]}: "{doc}"', "date": datetime.now()}
                await add_dialog_message(chat, new_dialog_message)
    except RuntimeError:
        text = f'{config.lang["errores"]["error"][lang]}: {config.lang["errores"]["tiempoagotado"][lang]}'
    await update.message.reply_text(f'{text}', parse_mode=ParseMode.MARKDOWN)
    await releasemaphore(chat=chat)
async def ocr_image_wrapper(update, context):
    chat = await chat_check(update, context)
    lang = await lang_check(update, context, chat)
    if not await is_bot_mentioned(update, context): return
    if await is_previous_message_not_answered_yet(chat, lang, update): return
    task = bb(ocr_image(chat, lang, update, context))
    bcs(handle_chat_task(chat, lang, task, update))

async def transcribe_message_handle(chat, lang, update, context):
    # Procesar sea voz o audio
    if update.message.voice:
        audio = update.message.voice
    elif update.message.audio:
        audio = update.message.audio
    file_size_mb = audio.file_size / (1024 * 1024)
    if file_size_mb <= config.audio_max_size:
        try:
            await update.effective_chat.send_action(ChatAction.TYPING)
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Descargar y convertir a MP3
                tmp_dir = Path(tmp_dir)
                ext = audio.mime_type
                import mimetypes
                if ext == 'audio/opus':
                    ext = '.opus'
                else:
                    ext = mimetypes.guess_extension(ext)
                doc_path = tmp_dir / Path("tempaudio" + ext)

                # download
                voice_file = await context.bot.get_file(audio.file_id)
                await voice_file.download_to_drive(doc_path)

                # convert to mp3
                mp3_file_path = tmp_dir / "voice.mp3"
                from pydub import AudioSegment
                AudioSegment.from_file(doc_path).export(mp3_file_path, format="mp3")

                # Transcribir
                with open(mp3_file_path, "rb") as f:
                    await releasemaphore(chat=chat)
                    transcribed_text = await openai_utils.ChatGPT(chat).transcribe_audio(f)

            # Enviar respuesta            
            text = f"🎤 {transcribed_text}"
            interaction_cache[chat.id] = ("visto", datetime.now())
            await db.set_chat_attribute(chat, "last_interaction", datetime.now())
        except Exception as e:
            logger.error(f'<transcribe_message_handle> {config.lang["errores"]["error"][lang]}: {e}')
            await releasemaphore(chat=chat)
            return
    else:
        text = f'{config.lang["errores"]["audio_size_limit"][lang].format(audio_max_size=config.audio_max_size)}'
    await send_large_message(text, update)
    await releasemaphore(chat=chat)
    await message_handle(chat, lang, update, context, _message=transcribed_text)
async def transcribe_message_wrapper(update, context):
    chat = await chat_check(update, context)
    lang = await lang_check(update, context, chat)
    if not await is_bot_mentioned(update, context): return
    if await is_previous_message_not_answered_yet(chat, lang, update): return
    task = bb(transcribe_message_handle(chat, lang, update, context))
    bcs(handle_chat_task(chat, lang, task, update))

async def generate_image_handle(chat, lang, update: Update, context: CallbackContext, _message=None):
    if _message:
        prompt = _message
    else:
        if not context.args:
            await update.message.reply_text(f'{config.lang["mensajes"]["genimagen_noargs"][lang]}', parse_mode=ParseMode.HTML)
            await releasemaphore(chat=chat)
            return
        else:
            prompt = ' '.join(context.args)
    if prompt == None:
        await update.message.reply_text(f'{config.lang["mensajes"]["genimagen_notext"][lang]}', parse_mode=ParseMode.HTML)
        await releasemaphore(chat=chat)
        return
    import openai
    try:
        await releasemaphore(chat=chat)
        await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
        image_urls = await openai_utils.ChatGPT(chat).generate_images(prompt)
    except (openai.error.APIError, openai.error.InvalidRequestError) as e:
        if "Request has inappropriate content!" in str(e) or "Your request was rejected as a result of our safety system." in str(e):
            text = f'{config.lang["errores"]["genimagen_rejected"][lang]}'
        else:
            text = f'{config.lang["errores"]["genimagen_other"][lang]}'
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        await releasemaphore(chat=chat)
        return
    except telegram.error.BadRequest as e:
        text = f'{config.lang["errores"]["genimagen_badrequest"][lang]}'
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        await releasemaphore(chat=chat)
        return

    image_group=[]
    document_group=[]
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    for i, image_url in enumerate(image_urls):
        image = InputMediaPhoto(image_url)
        image_group.append(image)
        document = InputMediaDocument(image_url, parse_mode=ParseMode.HTML, filename=f"imagen_{i}.png")
        document_group.append(document)
    await update.message.reply_media_group(image_group)
    await update.message.reply_media_group(document_group)
    interaction_cache[chat.id] = ("visto", datetime.now())
    await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    await releasemaphore(chat=chat)
async def generate_image_wrapper(update, context, _message=None, chat=None, lang=None):
    if not chat:
        chat = await chat_check(update, context)
    if not lang:
        lang = await lang_check(update, context, chat)
    if await is_previous_message_not_answered_yet(chat, lang, update): return
    task = bb(generate_image_handle(chat, lang, update, context, _message))
    bcs(handle_chat_task(chat, lang, task, update))

async def ask_timeout_handle(chat, lang, update: Update, _message):
    keyboard = [[
        InlineKeyboardButton("✅", callback_data="new_dialog|true"),
        InlineKeyboardButton("❎", callback_data="new_dialog|false"),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    new_dialog_message = {"user": _message, "date": datetime.now()}
    await add_dialog_message(chat, new_dialog_message)

    await update.effective_chat.send_message(f'{config.lang["mensajes"]["timeout_ask"][lang]}', reply_markup=reply_markup)
async def answer_timeout_handle(update: Update, context: CallbackContext):
    chat = await chat_check(update, context)
    lang = await lang_check(update, context, chat)
    query = update.callback_query
    await query.answer()
    new_dialog = query.data.split("|")[1]
    dialog_messages = await db.get_dialog_messages(chat, dialog_id=None)
    if len(dialog_messages) == 0:
        await update.effective_chat.send_message(f'{config.lang["mensajes"]["timeout_nodialog"][lang]}')
        await releasemaphore(chat=chat)
        await new_dialog_handle(update, context, chat, lang)
        return
    elif 'bot' in dialog_messages[-1]: # already answered, do nothing
        await releasemaphore(chat=chat)
        return
    await query.message.delete()
    if new_dialog == "true":
        last_dialog_message = dialog_messages.pop()
        await releasemaphore(chat=chat)
        await new_dialog_handle(update, context, chat, lang)
        await message_handle(chat, lang, update, context, _message=last_dialog_message["user"])
    else:
        await releasemaphore(chat=chat)
        await retry_handle(update, context, chat, lang)

async def cancel_handle(update: Update, context: CallbackContext, mensaje_actions=None):
    chat = await chat_check(update, context)
    lang = await lang_check(update, context, chat)
    semaphore = chat_locks.get(chat.id)
    if not semaphore and not semaphore.locked() or chat.id not in chat_tasks:
        text = config.lang["mensajes"]["nadacancelado"][lang]
        if mensaje_actions:
            await mensaje_actions.reply_text(text, reply_to_message_id=mensaje_actions.message_id, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML)
    else:
        await releasemaphore(chat)
        task = chat_tasks[chat.id]
        task.cancel()
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())

async def get_menu(menu_type, update: Update, context: CallbackContext, chat, page_index):
    try:
        lang = await lang_check(update, context, chat)
        menu_type_dict = getattr(config, menu_type)
        if chat.id in globals()[f"{menu_type}_cache"]:
            current_key = globals()[f"{menu_type}_cache"][chat.id][0]
        else:
            current_key = await db.get_chat_attribute(chat, f"current_{menu_type}")
            globals()[f"{menu_type}_cache"][chat.id] = (current_key, datetime.now())
        item_keys = await get_menu_item_keys(menu_type, menu_type_dict, chat, lang, update)
        if config.switch_imgs != "True" and "imagen" in item_keys:
            item_keys.remove("imagen")
        option_name = await get_menu_option_name(current_key, menu_type, menu_type_dict, lang)
        text = await get_menu_text(lang, option_name, menu_type, menu_type_dict, current_key)
        keyboard = await get_menu_keyboard(item_keys, page_index, menu_type, menu_type_dict, lang)
        reply_markup = InlineKeyboardMarkup(keyboard)
        return text, reply_markup
    except Exception as e:
        logger.error(f'<get_menu> {config.lang["errores"]["error"][lang]}: {e}')
async def get_menu_item_keys(menu_type, menu_type_dict, chat, lang, update):
    if menu_type != "model" and menu_type != "api":
        item_keys = menu_type_dict[f"available_{menu_type}"]
    elif menu_type == "api":
        item_keys = apis_vivas
    else:
        _, api_actual, _ = await parameters_check(chat, lang, update)
        item_keys = config.api["info"][api_actual]["available_model"]
    return item_keys

def convert_dict_to_immutable(d):
    if isinstance(d, dict):
        return frozenset((k, convert_dict_to_immutable(v)) for k, v in d.items())
    elif isinstance(d, list):
        return tuple(convert_dict_to_immutable(x) for x in d)
    else:
        return d
        
async def get_menu_keyboard(item_keys, page_index, menu_type, menu_type_dict, lang):
    
    menu_type_dict_immutable = convert_dict_to_immutable(menu_type_dict)
    cache_key = (tuple(item_keys), page_index, menu_type, menu_type_dict_immutable, lang)
    
    if cache_key in menu_cache:
        return menu_cache[cache_key]
    else:
        per_page = config.itemspage
        page_keys = item_keys[page_index * config.itemspage:(page_index + 1) * per_page]
        import math
        num_rows = math.ceil(len(page_keys) / config.columnpage)
    
        # Crear lista de tuplas para representar el teclado
        keyboard_data = []
        for index, current_key in enumerate(page_keys):
            name = await get_menu_item_name(menu_type, menu_type_dict, current_key, lang)
            callback_data = f"set_{menu_type}|{current_key}|{page_index}"
            keyboard_data.append((index, name, callback_data))
    
        # Convertir la lista de tuplas en una matriz bidimensional de botones InlineKeyboardButton
        keyboard = []
        for row in range(num_rows):
            buttons = [InlineKeyboardButton(name, callback_data=callback_data)
                       for index, name, callback_data in keyboard_data[row * config.columnpage:(row + 1) * config.columnpage]]
            keyboard.append(buttons)
    
        # Agregar botones de navegación, si es necesario
        if len(item_keys) > config.itemspage:
            is_first_page = (page_index == 0)
            is_last_page = ((page_index + 1) * config.itemspage >= len(item_keys))
            navigation_buttons = []
            if not is_first_page:
                navigation_buttons.append(InlineKeyboardButton("«", callback_data=f"set_{menu_type}|paginillas|{page_index - 1}"))
            if not is_last_page:
                navigation_buttons.append(InlineKeyboardButton("»", callback_data=f"set_{menu_type}|paginillas|{page_index + 1}"))
            keyboard.append(navigation_buttons)
        
        menu_cache[cache_key] = keyboard
        return keyboard
        
async def get_menu_item_name(menu_type, menu_type_dict, current_key, lang):
    if menu_type != "lang" and menu_type != "chat_mode":
        name = menu_type_dict["info"][current_key]["name"]
    elif menu_type == "chat_mode":
        name = menu_type_dict["info"][current_key]["name"][lang]
    else:
        name = menu_type_dict['info']['name'][current_key]
    return name
async def get_menu_text(lang, option_name, menu_type, menu_type_dict, current_key):
    if menu_type == "lang":
        description = menu_type_dict['info']['description'][lang]
    else:
        description = menu_type_dict['info'][current_key]['description'][lang]
    return f"<b>{config.lang['info']['actual'][lang]}</b>\n\n{str(option_name)}. {description}\n\n<b>{config.lang['info']['seleccion'][lang]}</b>:"
async def get_menu_option_name(current_key, menu_type, menu_type_dict, lang):
    if menu_type != "chat_mode" and menu_type != "lang":
        option_name = menu_type_dict["info"][current_key]["name"]
    elif menu_type == "chat_mode":
        option_name = menu_type_dict["info"][current_key]["name"][lang]
    else:
        option_name = menu_type_dict["info"]["name"][lang]  
    return option_name

async def menu_handler(update: Update):
    query = update.callback_query
    await query.answer()
    seleccion = query.data.split("|")[1]
    page_index = int(query.data.split("|")[2])
    if page_index < 0:
        return
    return query, page_index, seleccion

async def chat_mode_handle(update: Update, context: CallbackContext):
    try:
        chat = await chat_check(update, context)
        text, reply_markup = await get_menu(menu_type="chat_mode", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError:
        logger.error(f'<chat_mode_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]}')
async def chat_mode_callback_handle(update: Update, context: CallbackContext):
    query, page_index, _ = await menu_handler(update)
    await menu_edit_handler(query, update, context, page_index, menu_type="chat_mode")
async def set_chat_mode_handle(update: Update, context: CallbackContext):
    chat = await chat_check(update, context)
    lang = await lang_check(update, context, chat)
    query, page_index, seleccion = await menu_handler(update)
    if seleccion != "paginillas":
        if chat_mode_cache.get(chat.id)[0] != seleccion:
            chat_mode_cache[chat.id] = (seleccion, datetime.now())
            await db.set_chat_attribute(chat, "current_chat_mode", seleccion)
            await update.effective_chat.send_message(f"{config.chat_mode['info'][seleccion]['welcome_message'][lang]}", parse_mode=ParseMode.HTML)
    await menu_edit_handler(query, update, context, page_index, menu_type="chat_mode", chat=chat)
        
async def model_handle(update: Update, context: CallbackContext):
    try:
        chat = await chat_check(update, context)
        text, reply_markup = await get_menu(menu_type="model", update=update, context=context,chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError:
        logger.error(f'<model_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]}')
async def model_callback_handle(update: Update, context: CallbackContext):
    query, page_index, _ = await menu_handler(update)
    await menu_edit_handler(query, update, context, page_index, menu_type="model")
async def set_model_handle(update: Update, context: CallbackContext):
    chat = await chat_check(update, context)
    query, page_index, seleccion = await menu_handler(update)
    if seleccion != "paginillas":
        if model_cache.get(chat.id)[0] != seleccion:
            model_cache[chat.id] = (seleccion, datetime.now())
            await db.set_chat_attribute(chat, "current_model", seleccion)
    await menu_edit_handler(query, update, context, page_index, menu_type="model", chat=chat)
    
async def menu_edit_handler(query, update, context, page_index, menu_type, chat=None):
    if chat:
        argus = (menu_type, update, context, chat, page_index)
    else:
        argus = (menu_type, update, context, page_index)
    text, reply_markup = await get_menu(*argus)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except telegram.error.BadRequest as e:
        if str(e).startswith(msg_no_mod):
            # Ignorar esta excepción específica y continuar la ejecución normalmente
            pass
        else:
            # En caso de otras excepciones BadRequest, manejarlas adecuadamente o agregar acciones adicionales si es necesario
            raise
    
async def api_handle(update: Update, context: CallbackContext):
    try:
        chat = await chat_check(update, context)
        text, reply_markup = await get_menu(menu_type="api", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError:
        logger.error(f'<api_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]}')
async def api_callback_handle(update: Update, context: CallbackContext):
    query, page_index, _ = await menu_handler(update)
    await menu_edit_handler(query, update, context, page_index, menu_type="api")
async def set_api_handle(update: Update, context: CallbackContext):
    chat = await chat_check(update, context)
    query, page_index, seleccion = await menu_handler(update)
    if seleccion != "paginillas":
        if api_cache.get(chat.id)[0] != seleccion:
            api_cache[chat.id] = (seleccion, datetime.now())
            await db.set_chat_attribute(chat, "current_api", seleccion)
    await menu_edit_handler(query, update, context, page_index, menu_type="api", chat=chat)

async def lang_handle(update: Update, context: CallbackContext):
    try:
        chat = await chat_check(update, context)
        text, reply_markup = await get_menu(menu_type="lang", update=update, context=context, chat=chat, page_index=0)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError:
        logger.error(f'<lang_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]}')
async def lang_callback_handle(update: Update, context: CallbackContext):
    query, page_index, _ = await menu_handler(update)
    await menu_edit_handler(query, update, context, page_index, menu_type="lang")
async def set_lang_handle(update: Update, context: CallbackContext):
    chat = await chat_check(update, context)
    query, page_index, seleccion = await menu_handler(update)
    if seleccion != "paginillas":
        if lang_cache.get(chat.id)[0] != seleccion:
            lang_cache[chat.id] = (seleccion, datetime.now())
            await cambiar_idioma(update, context, chat, lang=seleccion)
    await menu_edit_handler(query, update, context, page_index, menu_type="lang", chat=chat)

async def error_handle(update: Update, context: CallbackContext) -> None:
    try:
        # Log the error with traceback
        logger.error(f'{config.lang["errores"]["handler_excepcion"][config.pred_lang]}:', exc_info=context.error)

        # Collect error message and traceback
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        update_str = json.dumps(update.to_dict(), indent=2, ensure_ascii=False)
        message = (
            f'{config.lang["errores"]["handler_excepcion"][config.pred_lang]}:\n'
            f'<pre>update = {html.escape(update_str)}</pre>\n\n'
            f'<pre>{html.escape(tb_string)}</pre>'
        )

        # Send error message
        await update.effective_chat.send_message(message, parse_mode='HTML')

    except Exception as e:
        # Handle errors that may occur during error handling
        error_message = f'{config.lang["errores"]["handler_error_handler"][config.pred_lang]}: {e}'
        logger.error(error_message)
        await update.effective_chat.send_message(error_message, parse_mode='HTML')

async def post_init(application: Application):
    bb(ejecutar_obtener_vivas())
    commandos = [
        ("/new", "🌟"),
        ("/chat_mode", "💬"),
        ("/retry", "🔄"),
        ("/model", "🧠"),
        ("/api", "🔌"),
        ("/lang", "🌍"),
        ("/help", "ℹ️")
    ]  
    if config.switch_imgs == "True":
        commandos.insert(5, ("/img", "🖼️"))
    await application.bot.set_my_commands(commandos)

async def ejecutar_obtener_vivas():
    while True:
        try:
            await obtener_vivas()
            for cache_name in cache_index:
                cache = locals().get(cache_name)
                if cache is not None:
                    await revisar_cache(cache)
        except asyncio.CancelledError:
            break
        await sleep(60 * config.apicheck_minutes)

def run_bot() -> None:
    try:
        application = (
            ApplicationBuilder()
            .token(config.telegram_token)
            .concurrent_updates(True)
            .rate_limiter(AIORateLimiter(max_retries=5))
            .post_init(post_init)
            .build()
        )
        # add handlers
        if config.user_whitelist:
            usernames = []
            user_ids = []
            for user in config.user_whitelist:
                user = user.strip()
                if user.isnumeric():
                    user_ids.append(int(user))
                else:
                    usernames.append(user)
            user_filter = filters.User(username=usernames) | filters.User(user_id=user_ids)
        else:
            user_filter = filters.ALL
        if config.chat_whitelist:
            chat_ids = []
            for chat in config.chat_whitelist:
                chat = chat.strip()
                if chat[0] == "-" and chat[1:].isnumeric():
                    chat_ids.append(int(chat))
            chat_filter = filters.Chat(chat_id=chat_ids)
        else:
            chat_filter = filters.ALL

        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & (user_filter | chat_filter), message_handle_wrapper))

        if config.switch_voice == "True":
            application.add_handler(MessageHandler(filters.AUDIO & (user_filter | chat_filter), transcribe_message_wrapper))
            application.add_handler(MessageHandler(filters.VOICE & (user_filter | chat_filter), transcribe_message_wrapper))
        if config.switch_ocr == "True":
            application.add_handler(MessageHandler(filters.PHOTO & (user_filter | chat_filter), ocr_image_wrapper))
        if config.switch_docs == "True":
            docfilter = (filters.Document.FileExtension("pdf") | filters.Document.FileExtension("lrc"))
            application.add_handler(MessageHandler(docfilter & (user_filter | chat_filter), document_wrapper))
            application.add_handler(MessageHandler(filters.Document.Category('text/') & (user_filter | chat_filter), document_wrapper))
        
        application.add_handler(CommandHandler("start", start_handle, filters=(user_filter | chat_filter)))
        application.add_handler(CommandHandler("help", help_handle, filters=(user_filter | chat_filter)))
        application.add_handler(CommandHandler("help_group_chat", help_group_chat_handle, filters=(user_filter | chat_filter)))
        application.add_handler(CommandHandler("retry", retry_handle, filters=(user_filter | chat_filter)))
        application.add_handler(CommandHandler("new", new_dialog_handle, filters=(user_filter | chat_filter)))
        application.add_handler(CommandHandler("cancel", cancel_handle, filters=(user_filter | chat_filter)))
        application.add_handler(CommandHandler("chat_mode", chat_mode_handle, filters=(user_filter | chat_filter)))
        application.add_handler(CommandHandler("model", model_handle, filters=(user_filter | chat_filter)))
        application.add_handler(CommandHandler("api", api_handle, filters=(user_filter | chat_filter)))
        if config.switch_imgs == "True":
            application.add_handler(CommandHandler("img", generate_image_wrapper, filters=(user_filter | chat_filter)))
        application.add_handler(CommandHandler("lang", lang_handle, filters=(user_filter | chat_filter)))
        application.add_handler(CallbackQueryHandler(set_lang_handle, pattern="^set_lang"))

        application.add_handler(CallbackQueryHandler(answer_timeout_handle, pattern="^new_dialog"))
        application.add_handler(CallbackQueryHandler(actions_handle, pattern="^action"))
        mcbc = "^get_menu"
        application.add_handler(CallbackQueryHandler(chat_mode_callback_handle, pattern=mcbc))
        application.add_handler(CallbackQueryHandler(set_chat_mode_handle, pattern="^set_chat_mode"))
        application.add_handler(CallbackQueryHandler(model_callback_handle, pattern=mcbc))
        application.add_handler(CallbackQueryHandler(set_model_handle, pattern="^set_model"))
        application.add_handler(CallbackQueryHandler(api_callback_handle, pattern=mcbc))
        application.add_handler(CallbackQueryHandler(set_api_handle, pattern="^set_api"))

        application.add_error_handler(error_handle)
        application.run_polling()
    except telegram.error.TimedOut:
        logger.error(f'{config.lang["errores"]["tiempoagotado"][config.pred_lang]}')
    except Exception as e:
        logger.error(f'<run_bot> {config.lang["errores"]["error"][config.pred_lang]}: {e}.')

if __name__ == "__main__":
    run_bot()
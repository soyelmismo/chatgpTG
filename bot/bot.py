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
    BotCommand
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

db = database.Database()
logger = logging.getLogger(__name__)
bb = asyncio.create_task
bcs = asyncio.ensure_future
loop = asyncio.get_event_loop()
sleep = asyncio.sleep
chat_locks = {}
chat_tasks = {}
apis_vivas = []
msg_no_mod = "Message is not modified"


async def obtener_vivas():
    from apistatus import estadosapi
    global apis_vivas
    apis_vivas = await estadosapi()

async def handle_chat_task(chat, lang, task, update):
    async with chat_locks[chat.id]:
        chat_tasks[chat.id] = task
        try:
            await acquiresemaphore(chat=chat)
            await task
        except asyncio.CancelledError:
            await update.effective_chat.send_message(f'{config.lang["mensajes"]["cancelado"][lang]}', parse_mode=ParseMode.HTML)
            await releasemaphore(chat=chat)
        else:
            await releasemaphore(chat=chat)
        finally:
            if chat.id in chat_tasks:
                del chat_tasks[chat.id]
                await releasemaphore(chat=chat)
async def acquiresemaphore(chat):
    lock = chat_locks.get(chat.id)
    if lock is None:
        lock = asyncio.Lock()  # Inicializa un nuevo bloqueo si no existe
        chat_locks[chat.id] = lock
    await lock.acquire()
async def releasemaphore(chat):
    lock = chat_locks.get(chat.id)
    if lock and lock.locked():
        lock.release()

async def is_previous_message_not_answered_yet(chat, lang, update: Update):
    semaphore = chat_locks.get(chat.id)
    if semaphore and semaphore.locked():
        text = f'{config.lang["mensajes"]["mensaje_semaforo"][lang]}'
        await update.message.reply_text(text, reply_to_message_id=update.message.id, parse_mode=ParseMode.HTML)
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
            db.new_dialog(chat)
            db.delete_all_dialogs_except_current(chat)
            #Bienvenido!
            await update.effective_chat.send_message(f"{config.chat_mode['info'][mododechat_actual]['welcome_message'][lang]}", parse_mode=ParseMode.HTML)
            db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except Exception as e:
        logger.error(f'<new_dialog_handle> {config.lang["errores"]["error"][lang]}: {e}')
    finally:
        await releasemaphore(chat=chat)

async def lang_check(update: Update, context: CallbackContext, chat=None):
    if chat is None:
        chat = await chat_check(update, context)
    if db.chat_exists(chat):
        lang = db.get_chat_attribute(chat, "current_lang")
    else:
        if update.effective_user.language_code in config.lang["available_lang"]:
            lang = update.effective_user.language_code
        else:
            lang = str(config.pred_lang)
    return lang
async def chat_check(update: Update, context: CallbackContext):
    if update.message:
        chat = update.message.chat
    elif update.callback_query:
        chat = update.callback_query.message.chat
    lang = await lang_check(update, context, chat)
    if not db.chat_exists(chat):
        db.add_chat(chat, lang)
        await cambiar_idioma(update, context, chat, lang)
        db.new_dialog(chat)
    if chat.id not in chat_locks:
        chat_locks[chat.id] = asyncio.Semaphore(1)
    return chat
async def parameters_check(chat, lang, update):
    # Verificar si hay valores inválidos en el usuario
    #chatmode
    mododechat_actual=db.get_chat_attribute(chat, 'current_chat_mode')
    if mododechat_actual not in config.chat_mode["available_chat_mode"]:
        mododechat_actual = config.chat_mode["available_chat_mode"][1]
        db.set_chat_attribute(chat, "current_chat_mode", mododechat_actual)
        await update.effective_chat.send_message(f'{config.lang["errores"]["reset_chat_mode"][lang].format(new=mododechat_actual)}')
    #api
    api_actual = db.get_chat_attribute(chat, 'current_api')
    if not apis_vivas:
        raise Exception(config.lang["errores"]["apis_vivas_not_ready_yet"][config.pred_lang])
    if api_actual not in apis_vivas:
        api_actual = apis_vivas[random.randint(0, len(apis_vivas) - 1)]
        db.set_chat_attribute(chat, "current_api", api_actual)
        await update.effective_chat.send_message(f'{config.lang["errores"]["reset_api"][lang].format(new=config.api["info"][api_actual]["name"])}')
    #model
    modelo_actual = db.get_chat_attribute(chat, 'current_model')
    modelos_disponibles=config.api["info"][api_actual]["available_model"]
    if modelo_actual not in modelos_disponibles:
        modelo_actual = modelos_disponibles[random.randint(0, len(modelos_disponibles) - 1)]
        db.set_chat_attribute(chat, "current_model", modelo_actual)
        await update.effective_chat.send_message(f'{config.lang["errores"]["reset_model"][lang].format(api_actual_name=config.api["info"][api_actual]["name"], new_model_name=config.model["info"][modelo_actual]["name"])}')
    return mododechat_actual, api_actual, modelo_actual

async def cambiar_idioma(update: Update, context: CallbackContext, chat=None, lang=None):
    if not chat:
        chat = await chat_check(update, context)
    if not lang:
        lang = await lang_check(update, context, chat)
    else:
        db.set_chat_attribute(chat, "current_lang", lang)
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

async def retry_handle(update: Update, context: CallbackContext, chat=None, lang=None):
    if not chat:
        chat = await chat_check(update, context)
    if not lang:
        lang = await lang_check(update, context, chat)
    if await is_previous_message_not_answered_yet(chat, lang, update): return
    dialog_messages = db.get_dialog_messages(chat, dialog_id=None)
    if len(dialog_messages) == 0:
        await releasemaphore(chat=chat)
        await update.message.reply_text(f'{config.lang["mensajes"]["no_retry_mensaje"][lang]}')
        return
    last_dialog_message = dialog_messages.pop()
    db.set_dialog_messages(chat, dialog_messages, dialog_id=None)  # last message was removed from the context
    db.set_chat_attribute(chat, "last_interaction", datetime.now())
    await releasemaphore(chat=chat)
    await message_handle(chat, lang, update, context, _message=last_dialog_message["user"])

async def check_message(update: Update, _message=None):
    if update.effective_chat.type == "private":
        raw_msg = _message or update.effective_message
        if isinstance(raw_msg, str):
            _message = raw_msg
            raw_msg = update.effective_chat
        elif hasattr(raw_msg, 'text'):
            _message = raw_msg.text
    else:  # En caso de que el mensaje provenga de un grupo
        raw_msg = update.effective_message
        _message = raw_msg.text if hasattr(raw_msg, 'text') else _message
    return raw_msg, _message

async def add_dialog_message(chat, new_dialog_message):
    db.set_dialog_messages(
        chat,
        db.get_dialog_messages(chat, dialog_id=None) + [new_dialog_message],
        dialog_id=None
    )

async def message_handle_wrapper(update, context):
    try:
        chat = await chat_check(update, context)
        lang = await lang_check(update, context, chat)
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
        try:
            if raw_msg.entities:
                urls = []
                for entity in raw_msg.entities:
                    if entity.type == 'url':
                        url_add = raw_msg.text[entity.offset:entity.offset+entity.length]
                        if "http://" in url_add or "https://" in url_add:
                            urls.append(raw_msg.text[entity.offset:entity.offset+entity.length])
                if urls:
                    await releasemaphore(chat=chat)
                    task = bb(url_handle(chat, lang, update, urls))
                    bcs(handle_chat_task(chat, lang, task, update))
                    return
        except AttributeError:
            pass
    dialog_messages = db.get_dialog_messages(chat, dialog_id=None)
    if (datetime.now() - db.get_chat_attribute(chat, "last_interaction")).seconds > config.dialog_timeout and len(dialog_messages) > 0:
        if config.timeout_ask == "True":
            await ask_timeout_handle(chat, lang, update, _message)
            return
        else:
            await new_dialog_handle(update, context, chat, lang)
            await update.effective_chat.send_message(f'{config.lang["mensajes"]["timeout_ask_false"][lang].format(chatmode=config.chat_mode["info"][chat_mode]["name"][lang])}', parse_mode=ParseMode.HTML)

    #remove bot mention (in group chats)
    if chat.type != "private":
        _message = _message.replace("@" + context.bot.username, "").strip()
        _message = f"{raw_msg.from_user.first_name}@{raw_msg.from_user.username}: {_message}"
    chat_mode = db.get_chat_attribute(chat, "current_chat_mode")
    current_model = db.get_chat_attribute(chat, "current_model")
    #await message_handle_fn(update, context, _message, chat, lang, dialog_messages, chat_mode, current_model)
    await releasemaphore(chat=chat)
    task = bb(message_handle_fn(update, context, _message, chat, lang, dialog_messages, chat_mode, current_model))
    bcs(handle_chat_task(chat, lang, task, update))
async def message_handle_fn(update, context, _message, chat, lang, dialog_messages, chat_mode, current_model):
    # in case of CancelledError
    try:
        # send placeholder message to chat
        placeholder_message = await update.effective_chat.send_message("🤔")
        # send typing action
        if chat:
            await update.effective_chat.send_action(ChatAction.TYPING)
        if _message is None or len(_message) == 0:
            await update.effective_chat.send_message(f'{config.lang["mensajes"]["message_empty_handle"][lang]}', parse_mode=ParseMode.HTML)
            return
        parse_mode = {
            "html": ParseMode.HTML,
            "markdown": ParseMode.MARKDOWN
        }[config.chat_mode["info"][chat_mode]["parse_mode"]]
        gen = openai_utils.ChatGPT(chat, model=current_model).send_message(_message, lang, dialog_messages, chat_mode)
        prev_answer = ""
        async for status, gen_answer in gen:                                                         
            answer = gen_answer[:4096]  # telegram message limit                                     
            # update only when 100 new symbols are ready                                             
            if abs(len(answer) - len(prev_answer)) < 150 and status != "finished":                    
                continue
            try:
                await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat.id, message_id=placeholder_message.message_id, parse_mode=parse_mode)
            except telegram.error.BadRequest as e:                                                   
                if str(e).startswith(msg_no_mod):                                     
                    continue
                else:
                    await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat.id, message_id=placeholder_message.message_id)
            await sleep(0.02)  # wait a bit to avoid flooding                                 
            prev_answer = answer
        # update chat data
        db.set_chat_attribute(chat, "last_interaction", datetime.now())
        new_dialog_message = {"user": _message, "bot": answer, "date": datetime.now()}
        await add_dialog_message(chat, new_dialog_message)
        await releasemaphore(chat=chat)
    except Exception as e:
        logger.error(f'<message_handle_fn> {config.lang["errores"]["error"][lang]}: {e}')
        await releasemaphore(chat=chat)
        await context.bot.edit_message_text(f'{config.lang["errores"]["error_inesperado"][lang]}', chat_id=placeholder_message.chat.id, message_id=placeholder_message.message_id)
        return
    if chat_mode == "imagen":
        await generate_image_wrapper(update, context, _message=answer, chat=chat, lang=lang)

async def send_large_message(text, update):
    if len(text) <= 4096:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    else:
        # Divide el mensaje en partes más pequeñas
        message_parts = [text[i:i+4096] for i in range(0, len(text), 4096)]
        for part in message_parts:
            await update.message.reply_text(part, parse_mode=ParseMode.HTML)

async def clean_text(doc):
    import re
    doc = re.sub(r'^\n', '', doc) 
    doc = re.sub(r'\n+', r' ', doc) # Reemplaza saltos de línea dentro de párrafos por un espacio  
    doc = re.sub(r' {2,}', ' ', doc) # Reemplaza dos o más espacios con uno solo
    doc = re.sub(r'\s+', ' ', doc).strip()
    #doc = "\n".join(line.strip() for line in doc.split("\n"))
    return doc

async def url_handle(chat, lang, update, urls):
    import requests
    from bs4 import BeautifulSoup
    import warnings
    warnings.filterwarnings("ignore")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.54"
    }
    for url in urls:
        await update.effective_chat.send_action(ChatAction.TYPING)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            if len(response.content) > config.url_max_size * (1024 * 1024):
                raise Exception(f'{config.lang["errores"]["url_size_exception"][lang]}')
            soup = BeautifulSoup(response.content, "html.parser")
            body_tag = soup.body
            if body_tag:
                doc = body_tag.get_text('\n')
            else:
                # Si no hay etiqueta <body>, obtener todo el contenido de la página
                doc = soup.get_text('\n')
            doc = await clean_text(doc)
            new_dialog_message = {"url": f'{url}: [{doc}]', "user": ".", "date": datetime.now()}
            await add_dialog_message(chat, new_dialog_message)
            text = f'{config.lang["mensajes"]["url_anotado_ask"][lang]}'
        except Exception as e:
            text = f'{config.lang["errores"]["url_size_limit"][lang]}: {e}.'
            logger.error(text)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    db.set_chat_attribute(chat, "last_interaction", datetime.now())
    await releasemaphore(chat=chat)

async def document_handle(chat, lang, update, context):
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
                    text = f'{config.lang["errores"]["pdf_pages_limit"][lang].format(paginas=paginas, pdf_page_lim=config.pdf_page_lim)}'
                    paginas = config.pdf_page_lim - 1
                    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
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
            db.set_chat_attribute(chat, "last_interaction", datetime.now())
    else:
        text = f'{config.lang["errores"]["document_size_limit"][lang].replace("{file_size_mb}", f"{file_size_mb:.2f}").replace("{file_max_size}", str(config.file_max_size))}'
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
            db.set_chat_attribute(chat, "last_interaction", datetime.now())
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
            db.set_chat_attribute(chat, "last_interaction", datetime.now())
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
    db.set_chat_attribute(chat, "last_interaction", datetime.now())
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
    dialog_messages = db.get_dialog_messages(chat, dialog_id=None)
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

async def cancel_handle(update: Update, context: CallbackContext):
    chat = await chat_check(update, context)
    lang = await lang_check(update, context, chat)
    semaphore = chat_locks.get(chat.id)
    if semaphore and semaphore.locked():
        await releasemaphore(chat)
        if chat.id in chat_tasks:
            task = chat_tasks[chat.id]
            task.cancel()
        db.set_chat_attribute(chat, "last_interaction", datetime.now())
    else:
        await update.message.reply_text(f'{config.lang["mensajes"]["nadacancelado"][lang]}', parse_mode=ParseMode.HTML)

async def get_menu(menu_type, update: Update, context: CallbackContext, chat):
    try:
        lang = await lang_check(update, context, chat)
        menu_type_dict = getattr(config, menu_type)
        _, api_actual, _ = await parameters_check(chat, lang, update)
        current_key = db.get_chat_attribute(chat, f"current_{menu_type}")
        if menu_type == "model":
            item_keys = config.api["info"][api_actual]["available_model"]
        elif menu_type == "api":
            item_keys = apis_vivas
        else:
            item_keys = menu_type_dict[f"available_{menu_type}"]
        if menu_type == "chat_mode":
            option_name = menu_type_dict["info"][current_key]["name"][lang]
        elif menu_type == "lang":
            option_name = menu_type_dict["info"]["name"][lang]
        else:
            option_name = menu_type_dict["info"][current_key]["name"]
        text = f"<b>{config.lang['info']['actual'][lang]}</b>\n\n{str(option_name)}. {config.lang['info']['description'][lang] if menu_type == 'lang' else menu_type_dict['info'][current_key]['description'][lang]}\n\n<b>{config.lang['info']['seleccion'][lang]}</b>:"
        num_cols = 2
        import math
        num_rows = math.ceil(len(item_keys) / num_cols)
        options = [
            [
            menu_type_dict["info"][current_key]["name"][lang] if menu_type == "chat_mode" else (config.lang['info']['name'][current_key] if menu_type == 'lang' else menu_type_dict["info"][current_key]["name"]),
            f"set_{menu_type}|{current_key}",
            current_key,
            ]
            for current_key in item_keys
        ]
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(name, callback_data=data) 
                    for name, data, selected in options[i::num_rows]
                ]
                for i in range(num_rows)
            ]
        )
        return text, reply_markup
    except Exception as e:
        logger.error(f'<get_menu> {config.lang["errores"]["error"][lang]}: {e}')

async def chat_mode_handle(update: Update, context: CallbackContext):
    try:
        chat = await chat_check(update, context)
        text, reply_markup = await get_menu(menu_type="chat_mode", update=update, context=context, chat=chat)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError:
        logger.error(f'<chat_mode_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]}')

async def chat_mode_callback_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    text, reply_markup = await get_menu(menu_type="chat_mode", update=update, context=context)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        if str(e).startswith(msg_no_mod):
            pass

async def set_chat_mode_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = await chat_check(update, context)
    await query.answer()
    mode = query.data.split("|")[1]
    db.set_chat_attribute(chat, "current_chat_mode", mode)
    text, reply_markup = await get_menu(menu_type="chat_mode", update=update, context=context, chat=chat)
    try:
        lang = await lang_check(update, context, chat)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        await update.effective_chat.send_message(f"{config.chat_mode['info'][db.get_chat_attribute(chat, 'current_chat_mode')]['welcome_message'][lang]}", parse_mode=ParseMode.HTML)
        db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except telegram.error.BadRequest as e:
        if str(e).startswith(msg_no_mod):
            pass

async def model_handle(update: Update, context: CallbackContext):
    try:
        chat = await chat_check(update, context)
        text, reply_markup = await get_menu(menu_type="model", update=update, context=context,chat=chat)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError:
        logger.error(f'<model_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]}')

async def model_callback_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    text, reply_markup = await get_menu(menu_type="model", update=update, context=context)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        if str(e).startswith(msg_no_mod):
            pass

async def set_model_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = await chat_check(update, context)
    await query.answer()
    _, model = query.data.split("|")
    db.set_chat_attribute(chat, "current_model", model)
    text, reply_markup = await get_menu(menu_type="model", update=update, context=context, chat=chat)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except telegram.error.BadRequest as e:
        if str(e).startswith(msg_no_mod):
            pass

async def api_handle(update: Update, context: CallbackContext):
    try:
        chat = await chat_check(update, context)
        text, reply_markup = await get_menu(menu_type="api", update=update, context=context, chat=chat)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError:
        logger.error(f'<api_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]}')

async def api_callback_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    text, reply_markup = await get_menu(menu_type="api", update=update, context=context)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        if str(e).startswith(msg_no_mod):
            pass

async def set_api_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = await chat_check(update, context)
    await query.answer()
    _, api = query.data.split("|")
    db.set_chat_attribute(chat, "current_api", api)
    text, reply_markup = await get_menu(menu_type="api", update=update, context=context, chat=chat)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except telegram.error.BadRequest as e:
        if str(e).startswith(msg_no_mod):
            pass

async def error_handle(update: Update, context: CallbackContext) -> None:
    logger.error(msg=f'{config.lang["errores"]["handler_excepcion"][config.pred_lang]}:', exc_info=context.error)
    try:
        # collect error message
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f'{config.lang["errores"]["handler_excepcion"][config.pred_lang]}:\n'
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )
    except:
        await context.bot.send_message(f'{config.lang["errores"]["handler_error_handler"][config.pred_lang]}')

async def post_init(application: Application):
    bb(ejecutar_obtener_vivas())
    commandos = [
        BotCommand("/new", "🌟"),
        BotCommand("/chat_mode", "💬"),
        BotCommand("/retry", "🔄"),
        BotCommand("/model", "🧠"),
        BotCommand("/api", "🔌"),
        BotCommand("/img", "🖼️"),
        BotCommand("/lang", "🌍"),
        BotCommand("/help", "ℹ️")
    ]
    await application.bot.set_my_commands(commandos)

async def lang_handle(update: Update, context: CallbackContext):
    try:
        chat = await chat_check(update, context)
        text, reply_markup = await get_menu(menu_type="lang", update=update, context=context, chat=chat)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except TypeError:
        logger.error(f'<lang_handle> {config.lang["errores"]["error"][config.pred_lang]}: {config.lang["errores"]["menu_modes_not_ready_yet"][config.pred_lang]}')

async def lang_callback_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    text, reply_markup = await get_menu(menu_type="lang", update=update, context=context)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        if str(e).startswith(msg_no_mod):
            pass

async def set_lang_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = await chat_check(update, context)
    await query.answer()
    _, lang = query.data.split("|")
    await cambiar_idioma(update, context, chat, lang)
    text, reply_markup = await get_menu(menu_type="lang", update=update, context=context, chat=chat)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except telegram.error.BadRequest as e:
        if str(e).startswith(msg_no_mod):
            pass

async def ejecutar_obtener_vivas():
    while True:
        try:
            await obtener_vivas()
        except asyncio.CancelledError:
            break
        await sleep(60 * config.apicheck_minutes)  # Cada 60 segundos * 60 minutos

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
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, message_handle_wrapper))
        application.add_handler(MessageHandler(filters.AUDIO & user_filter, transcribe_message_wrapper))
        application.add_handler(MessageHandler(filters.VOICE & user_filter, transcribe_message_wrapper))
        application.add_handler(MessageHandler(filters.PHOTO & user_filter, ocr_image_wrapper))
        docfilter = (filters.Document.FileExtension("pdf") | filters.Document.FileExtension("lrc"))
        application.add_handler(MessageHandler(docfilter & user_filter, document_wrapper))
        application.add_handler(MessageHandler(filters.Document.Category('text/') & user_filter, document_wrapper))
        
        application.add_handler(CommandHandler("start", start_handle, filters=user_filter))
        application.add_handler(CommandHandler("help", help_handle, filters=user_filter))
        application.add_handler(CommandHandler("help_group_chat", help_group_chat_handle, filters=user_filter))
        application.add_handler(CommandHandler("retry", retry_handle, filters=user_filter))
        application.add_handler(CommandHandler("new", new_dialog_handle, filters=user_filter))
        application.add_handler(CommandHandler("cancel", cancel_handle, filters=user_filter))
        application.add_handler(CommandHandler("chat_mode", chat_mode_handle, filters=user_filter))
        application.add_handler(CommandHandler("model", model_handle, filters=user_filter))
        application.add_handler(CommandHandler("api", api_handle, filters=user_filter))
        application.add_handler(CommandHandler("img", generate_image_wrapper, filters=user_filter))
        application.add_handler(CommandHandler("lang", lang_handle, filters=user_filter))
        application.add_handler(CallbackQueryHandler(set_lang_handle, pattern="^set_lang"))

        application.add_handler(CallbackQueryHandler(answer_timeout_handle, pattern="^new_dialog"))
        application.add_handler(CallbackQueryHandler(chat_mode_callback_handle, pattern="^get_menu"))
        application.add_handler(CallbackQueryHandler(set_chat_mode_handle, pattern="^set_chat_mode"))
        application.add_handler(CallbackQueryHandler(model_callback_handle, pattern="^get_menu"))
        application.add_handler(CallbackQueryHandler(set_model_handle, pattern="^set_model"))
        application.add_handler(CallbackQueryHandler(api_callback_handle, pattern="^get_menu"))
        application.add_handler(CallbackQueryHandler(set_api_handle, pattern="^set_api"))

        application.add_error_handler(error_handle)
        application.run_polling()
    except telegram.error.TimedOut:
        logger.error(f'{config.lang["errores"]["tiempoagotado"][config.pred_lang]}')
    except Exception as e:
        logger.error(f'<run_bot> {config.lang["errores"]["error"][config.pred_lang]}: {e}.')

if __name__ == "__main__":
    run_bot()
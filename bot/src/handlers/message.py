from bot.src.start import Update, CallbackContext
from bot.src.utils.gen_utils.phase import ChatGPT
from bot.src.utils.checks.c_message import check as check_message
from bot.src.utils.misc import update_dialog_messages
from bot.src.utils.constants import constant_db_model, constant_db_chat_mode

from bot.src.handlers import semaphore as tasks
from datetime import datetime
from . import url, timeout
from .commands import new
from .commands import img, cancel, retry

async def wrapper(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (debe_continuar,parametros,obtener_contextos as oc,bb,logger,config)
    if update.edited_message: return
    chat, lang = await oc(update)
    try:
        # check if bot was mentioned (for groups)
        if not await debe_continuar(chat, lang, update, context): return
        task = bb(handle(chat, lang, update, context))
        await tasks.handle(chat, lang, task, update)
    except Exception as e:
        logger.error(f'<message_handle_wrapper> {config.lang["errores"]["error"][lang]}: {e}')
async def handle(chat, lang, update, context, _message=None, msgid=None):
    from bot.src.utils.proxies import parametros, bb, chat_mode_cache, db, interaction_cache, model_cache, config, ParseMode
    await parametros(chat, lang, update)
    if _message:
        raw_msg, _ = await check_message(update, _message)
        raw_msg = raw_msg[0]
    else:
        raw_msg, _message = await check_message(update, _message)
        if chat.type != "private":
            _message = _message.replace("@" + context.bot.username, "").strip()
            _message = f"{raw_msg.from_user.first_name}: {_message}"
    if await process_urls(raw_msg, chat, lang, update):
        return
    dialog_messages = await db.get_dialog_messages(chat, dialog_id=None)
    chat_mode = (chat_mode_cache.get(chat.id)[0] if chat.id in chat_mode_cache else
                await db.get_chat_attribute(chat, f'{constant_db_chat_mode}'))
    chat_mode_cache[chat.id] = (chat_mode, datetime.now())
    if chat.id in interaction_cache:
        last_interaction = interaction_cache[chat.id][1]
    else:
        last_interaction = await db.get_chat_attribute(chat, "last_interaction")
    if (datetime.now() - last_interaction).seconds > config.dialog_timeout and len(dialog_messages) > 0:
        if config.timeout_ask:
            await timeout.ask(chat, lang, update, _message)
            return
        else:
            await new.handle(update, context)
            await update.effective_chat.send_message(f'{config.lang["mensajes"]["timeout_ask_false"][lang].format(chatmode=config.chat_mode["info"][chat_mode]["name"][lang])}', parse_mode=ParseMode.HTML)
    if chat.id in model_cache:
        current_model = model_cache[chat.id][0]
    else:
        current_model = await db.get_chat_attribute(chat, f'{constant_db_model}')
        model_cache[chat.id] = (current_model, datetime.now())
    await tasks.releasemaphore(chat=chat)
    task = bb(gen(update, context, _message, chat, lang, dialog_messages, chat_mode, current_model, msgid))
    await tasks.handle(chat, lang, task, update)

async def gen(update, context, _message, chat, lang, dialog_messages, chat_mode, current_model, msgid):
    from bot.src.utils.proxies import (bb,logger,db,interaction_cache,msg_no_mod,sleep,config,ParseMode,ChatAction,telegram)
    from bot.src.utils.constants import continue_key
    # Funciones auxiliares
    async def send_error_message():
        await update.effective_chat.send_message(f'{config.lang["mensajes"]["message_empty_handle"][lang]}', parse_mode=ParseMode.HTML)
    async def get_update_params():
        if chat.type != "private":
            return 250, 0.1
        else:
            return 75, 0.5
    async def get_parse_mode():
        return {
            "html": ParseMode.HTML,
            "markdown": ParseMode.MARKDOWN
        }[config.chat_mode["info"][chat_mode]["parse_mode"]]
    async def get_keyboard():
        keyboard = [[]]
        keyboard[0].append({"text": "🚫", "callback_data": "actions|cancel"})
        return keyboard
    async def update_placeholder_message(answer, keyboard):
        try:
            await context.bot.edit_message_text(telegram.helpers.escape_markdown(f'{answer}...⏳', version=1), chat_id=placeholder_message.chat.id, message_id=placeholder_message.message_id, disable_web_page_preview=True, reply_markup={"inline_keyboard": keyboard}, parse_mode=parse_mode)
        except telegram.error.BadRequest as e:
            if str(e).startswith(msg_no_mod):
                pass
            else:
                await context.bot.edit_message_text(telegram.helpers.escape_markdown(f'{answer}...⏳', version=1), chat_id=placeholder_message.chat.id, message_id=placeholder_message.message_id, disable_web_page_preview=True, reply_markup={"inline_keyboard": keyboard}, parse_mode=parse_mode)
    async def get_reply_id(update, msgid=None):
        if msgid:
            return msgid
        elif chat.type != "private" or _message == continue_key:
            return update.effective_message.message_id
        return None
    # Verificar si el mensaje está vacío
    if not _message:
        await send_error_message()
        return
    # Configurar parámetros de actualización
    upd, timer = await get_update_params()
    # Configurar modo de análisis de mensajes
    parse_mode = await get_parse_mode()
    # Configurar teclado
    keyboard = await get_keyboard()
    # Enviar mensaje de espera
    await update.effective_chat.send_action(ChatAction.TYPING)
    reply_val = await get_reply_id(update, msgid)
    placeholder_message = await update.effective_chat.send_message("🤔...",  reply_markup={"inline_keyboard": keyboard}, reply_to_message_id=reply_val)
    # Generar respuesta
    prev_answer = ""
    answer = ""
    insta = ChatGPT(chat, lang, model=current_model)
    gen = insta.send_message(_message, dialog_messages, chat_mode)
    while True:
        try:
            status, gen_answer = await gen.asend(None)
            answer = gen_answer[:4096]  # telegram message limit
            if abs(len(answer) - len(prev_answer)) < upd and status != "finished":
                continue
            await update_placeholder_message(answer, keyboard)
            await sleep(timer)  # Esperar un poco para evitar el flooding
            prev_answer = answer
            if status == "finished":
                break
        except StopAsyncIteration:
            break
    # Actualizar mensaje de chat con la respuesta generada
    keyboard[0].append({"text": "🔄", "callback_data": "actions|retry"})
    keyboard[0].append({"text": "▶️", "callback_data": "actions|continuar"})
    await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat.id, message_id=placeholder_message.message_id, disable_web_page_preview=True, reply_markup={"inline_keyboard": keyboard}, parse_mode=parse_mode)
    # Actualizar caché de interacciones y historial de diálogos del chat
    interaction_cache[chat.id] = ("visto", datetime.now())
    await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    _message = " " if _message == continue_key or _message==None else _message
    answer = " " if answer == None else answer
    new_dialog_message = {"user": _message, "bot": answer, "date": datetime.now()}
    advertencia = await update_dialog_messages(chat, new_dialog_message)
    if advertencia==True:
        await update.effective_chat.send_message(f'{config.lang["errores"]["advertencia_tokens_excedidos"][lang]}', reply_to_message_id=reply_val)
    # Liberar semáforo
    await tasks.releasemaphore(chat=chat)
    # Manejar excepciones
    try:
        if config.switch_imgs == "True" and chat_mode == "imagen":
            task = bb(img.wrapper(update, context, _message=answer))
            await tasks.handle(chat, lang, task, update)
    except Exception as e:
        logger.error(f'<message_handle_fn> {config.lang["errores"]["error"][lang]}: {e}')
        keyboard = []
        keyboard.append([])
        keyboard[0].append({"text": "🔄", "callback_data": "actions|retry"})
        await context.bot.edit_message_text(f'{answer}\n\n{config.lang["errores"]["error_inesperado"][lang]}', chat_id=placeholder_message.chat.id, message_id=placeholder_message.message_id, reply_markup={"inline_keyboard": keyboard})
    finally:
        await tasks.releasemaphore(chat=chat)

async def actions(update, context):
    from bot.src.utils.proxies import (obtener_contextos as oc, debe_continuar)
    from bot.src.utils.constants import continue_key
    chat, lang = await oc(update)
    query = update.callback_query
    await query.answer()
    action = query.data.split("|")[1]
    msgid = query.message.reply_to_message.message_id if query.message.reply_to_message is not None else None
    if action == "cancel":
        await cancel.handle(update, context)
    elif action == "continuar":
        if not await debe_continuar(chat, lang, update, context, bypassmention=True): return
        await handle(chat, lang, update, context, _message=continue_key, msgid=msgid)
    else:
        await retry.handle(update=update, context=context)

async def process_urls(raw_msg, chat, lang, update):
    from bot.src.utils.proxies import config
    try:
        if raw_msg.entities and config.switch_urls == "True":
            urls = await url.wrapper(raw_msg)
            if urls:
                textomensaje = await url.handle(chat, lang, update, urls)
                await update.effective_chat.send_message(textomensaje, reply_to_message_id=update.effective_message.message_id)
                await tasks.releasemaphore(chat=chat)
                return True
    except AttributeError:
        pass
    return False
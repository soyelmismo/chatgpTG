import logging
import asyncio
from bot.src.utils import config, database
import telegram
from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode, ChatAction
import re
from datetime import datetime
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

apis_vivas = config.api["available_api"]
msg_no_mod = "Message is not modified"

#contexts and checkers
async def obtener_contextos(update, chat=None, lang=None):
    from bot.src.utils.checks import c_chat, c_lang
    chat = await c_chat.check(update) if not chat else chat
    lang = await c_lang.check(update, chat) if not lang else lang
    if not await db.chat_exists(chat):
        await db.add_chat(chat, lang)
        from bot.src.handlers.commands.lang import cambiar_idioma
        await cambiar_idioma(update, chat, lang)
        await db.new_dialog(chat)
    if chat.id not in chat_locks: chat_locks[chat.id] = asyncio.Semaphore(1)
    return chat, lang

async def debe_continuar(chat, lang, update, context):
    from bot.src.utils.checks import c_bot_mentioned, c_message_not_answered_yet
    if not await c_bot_mentioned.check(update, context): return False
    if await c_message_not_answered_yet.check(chat, lang, update): return False
    return True
async def parametros(chat, lang, update):
    from bot.src.utils.checks import c_parameters
    mododechat_actual, api_actual, modelo_actual = await c_parameters.check(chat, lang, update)
    return mododechat_actual, api_actual, modelo_actual
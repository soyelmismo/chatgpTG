from bot.src.utils.constants import logger
import asyncio
from bot.src.utils import config, database
import telegram
from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode, ChatAction
import re
db = database.Database()
bb = asyncio.create_task
bcs = asyncio.ensure_future
loop = asyncio.get_event_loop()
sleep = asyncio.sleep
chat_locks = {}
chat_tasks = {}

#cache testing
cache_index = ["lang_cache", "chat_mode_cache", "api_cache", "model_cache",
               "menu_cache", "interaction_cache", "image_api_cache", "image_api_styles_cache",
               "image_styles_cache"]
lang_cache = {}
chat_mode_cache = {}
api_cache = {}
image_api_cache = {}
image_api_styles_cache = {}
image_styles_cache = {}
imaginepy_ratios_cache = {}
imaginepy_styles_cache = {}
imaginepy_models_cache = {}
model_cache = {}
menu_cache = {}
interaction_cache = {}

user_names = {}

msg_no_mod = "Message is not modified"

#contexts and checkers
async def obtener_contextos(update, chat=None, lang=None):
    from bot.src.utils.checks import c_chat, c_lang
    chat = await c_chat.check(update) if not chat else chat
    lang = await c_lang.check(update, chat) if not lang else lang
    if not await db.chat_exists(chat):
        await db.add_chat(chat, lang)
        await db.new_dialog(chat)
        from bot.src.handlers.commands.lang import cambiar_idioma
        await cambiar_idioma(update, chat, lang)
    if chat.id not in chat_locks: chat_locks[chat.id] = asyncio.Semaphore(1)
    return chat, lang

async def debe_continuar(chat, lang, update, context, bypassmention=None):
    from bot.src.utils.checks import c_bot_mentioned, c_message_not_answered_yet
    if not bypassmention and not await c_bot_mentioned.check(update, context): return False
    if await c_message_not_answered_yet.check(chat, lang, update): return False
    return True
async def parametros(chat, lang, update):
    from bot.src.utils.checks import c_parameters
    checked_chat_mode, checked_api, checked_model, checked_image_api, checked_image_styles, checked_imaginepy_ratios, checked_imaginepy_models = await c_parameters.check(chat, lang, update)
    return checked_chat_mode, checked_api, checked_model, checked_image_api, checked_image_styles, checked_imaginepy_ratios, checked_imaginepy_models

errorpredlang = config.lang[config.pred_lang]["errores"]["error"]
menusnotready = config.lang[config.pred_lang]["errores"]["menu_modes_not_ready_yet"]
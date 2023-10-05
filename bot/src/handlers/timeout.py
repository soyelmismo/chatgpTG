from bot.src.start import Update, CallbackContext

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from datetime import datetime
from . import semaphore as tasks
from bot.src.utils.misc import update_dialog_messages
from bot.src.utils.constants import logger
from .commands import new, retry
from . import message
async def ask(chat, lang, update: Update, _message):
    from bot.src.utils.proxies import (config)
    try:
        keyboard = [[
            InlineKeyboardButton("✅", callback_data="new_dialog|true"),
            InlineKeyboardButton("❎", callback_data="new_dialog|false"),
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        new_dialog_message = {"user": _message, "date": datetime.now()}
        await update_dialog_messages(chat, new_dialog_message)

        await update.effective_chat.send_message(f'{config.lang[lang]["mensajes"]["timeout_ask"]}', reply_markup=reply_markup)
    except Exception as e:
        logger.error(f'Timeout.ask > {e}')

async def answer(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,db,config)
    try:
        chat, lang = await oc(update)
        query = update.callback_query
        await query.answer()
        new_dialog = query.data.split("|")[1]
        dialog_messages = await db.get_dialog_messages(chat, dialog_id=None)
        await tasks.releasemaphore(chat=chat)
        if len(dialog_messages) == 0:
            await update.effective_chat.send_message(f'{config.lang[lang]["mensajes"]["timeout_nodialog"]}')
            await new.handle(update, context)
            return
        elif 'bot' in dialog_messages[-1]: # already answered, do nothing
            return
        await query.message.delete()
        if new_dialog == "true":
            last_dialog_message = dialog_messages.pop()
            await new.handle(update, context)
            await message.handle(chat, lang, update, context, _message=last_dialog_message["user"])
        elif new_dialog == "false": await retry.handle(update, context)
    except Exception as e:
        logger.error(f'Timeout.answer > {e}')
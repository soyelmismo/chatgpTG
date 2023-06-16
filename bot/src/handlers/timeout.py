from bot.src.start import Update, CallbackContext

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from datetime import datetime
from . import semaphore as tasks
from bot.src.utils.misc import update_dialog_messages
from .commands import new, retry
from . import message
async def ask(chat, lang, update: Update, _message):
    from bot.src.utils.proxies import (config)
    keyboard = [[
        InlineKeyboardButton("✅", callback_data="new_dialog|true"),
        InlineKeyboardButton("❎", callback_data="new_dialog|false"),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    new_dialog_message = {"user": _message, "date": datetime.now()}
    _ = await update_dialog_messages(chat, new_dialog_message)

    await update.effective_chat.send_message(f'{config.lang["mensajes"]["timeout_ask"][lang]}', reply_markup=reply_markup)
async def answer(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (obtener_contextos as oc,db,config)
    chat, lang = await oc(update)
    query = update.callback_query
    await query.answer()
    new_dialog = query.data.split("|")[1]
    dialog_messages = await db.get_dialog_messages(chat, dialog_id=None)
    if len(dialog_messages) == 0:
        await update.effective_chat.send_message(f'{config.lang["mensajes"]["timeout_nodialog"][lang]}')
        await tasks.releasemaphore(chat=chat)
        await new.handle(update, context, chat, lang)
        return
    elif 'bot' in dialog_messages[-1]: # already answered, do nothing
        await tasks.releasemaphore(chat=chat)
        return
    await query.message.delete()
    if new_dialog == "true":
        last_dialog_message = dialog_messages.pop()
        await tasks.releasemaphore(chat=chat)
        await new.handle(update, context, chat, lang)
        await message.handle(chat, lang, update, context, _message=last_dialog_message["user"])
    else:
        await tasks.releasemaphore(chat=chat)
        await retry.handle(update, context, chat, lang)
from datetime import datetime
from bot.src.start import Update, CallbackContext
from bot.src.handlers import semaphore as tasks
from bot.src.utils.constants import logger
async def handle(update: Update, context: CallbackContext, msgid=None):
    from bot.src.utils.proxies import (
    obtener_contextos as oc, debe_continuar, parametros,
    config, ParseMode,
    interaction_cache, db, errorpredlang
    )
    try:
        chat, lang = await oc(update)
        if not await debe_continuar(chat, lang, update, context): return
        mododechat_actual, _, _, _, _, _, _ = await parametros(chat, lang, update)
        await db.new_dialog(chat)
        await db.delete_all_dialogs_except_current(chat)
        #Bienvenido!
        await update.effective_chat.send_message(f"{config.chat_mode['info'][mododechat_actual]['welcome_message'][lang]}", parse_mode=ParseMode.HTML) if not msgid else None
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except Exception as e: logger.error(f'{__name__}: <new_dialog_handle> {errorpredlang}: {e}')
    finally: await tasks.releasemaphore(chat=chat)
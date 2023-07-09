import telegram
from telegram import Update
from telegram.ext import CallbackContext
from json import dumps
from html import escape
from traceback import format_exception
from bot.src.utils.proxies import config, ParseMode, errorpredlang
from bot.src.utils.constants import logger
async def handle(update: Update, context: CallbackContext) -> None:
    try:
        # Log the error with traceback
        logger.error(f'{__name__}: {config.lang[config.pred_lang]["errores"]["handler_excepcion"]}:', exc_info=context.error)

        # Collect error message and traceback
        tb_list = format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        update_str = dumps(update.to_dict(), indent=2, ensure_ascii=False)
        message = (
            f'{config.lang[config.pred_lang]["errores"]["handler_excepcion"]}:\n'
            f'<pre>update = {escape(update_str)}</pre>\n\n'
            f'<pre>{escape(tb_string)}</pre>'
        )

        # Send error message
        await update.effective_chat.send_message(message, parse_mode='HTML')
    except Exception as e:
        # Handle errors that may occur during error handling
        e = f'{config.lang[config.pred_lang]["errores"]["handler_error_handler"]}: {e}'
    finally:
        await send_error_msg(e)
        

async def mini_handle(e, lang, chat, update=None):
    from bot.src.handlers import semaphore
    if "Request has inappropriate content!" in str(e) or "Your request was rejected as a result of our safety system." in str(e):
        text = f'{config.lang[lang]["errores"]["genimagen_rejected"]}'
    else:
        text = f'{config.lang[lang]["errores"]["genimagen_other"]}'
    if update:
        await update.effective_chat.send_message(text, parse_mode=ParseMode.HTML, reply_to_message_id=update.effective_message.message_id)
    await semaphore.releasemaphore(chat=chat)
    await send_error_msg(e)

async def send_error_msg(e):
    logger.error(f'{__name__}: {errorpredlang}: {e}')
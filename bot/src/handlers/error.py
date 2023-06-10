from bot.src.start import Update, CallbackContext

import traceback, html, json
async def handle(update: Update, context: CallbackContext) -> None:
    from bot.src.utils.proxies import logger, config
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
        logger.error(f'{config.lang["errores"]["handler_error_handler"][config.pred_lang]}: {e}')
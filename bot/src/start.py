import telegram
from telegram import Update
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
from .handlers import message, voice, ocr_image, document, timeout, error
from .handlers.commands import (
start, help, retry, new, cancel, chat_mode, model,
api, img, lang, status, reset, search, props, istyle, iratio)
from .handlers.callbacks import imagine
from .tasks import cache
from .utils import config
from .utils.proxies import bb, logger

async def post_init(application: Application):
    bb(cache.task())
    commandos = [
        ("/new", "🌟"),
        ("/props", "⚙️"),
        ("/retry", "🔄"),
        ("/help", "ℹ️")
    ]
    if config.switch_imgs == True:
        commandos.insert(1, ("/img", "🎨"))
    if config.switch_search == True:
        commandos.insert(2, ("/search", "🔎"))
    await application.bot.set_my_commands(commandos)
    print(f'-----{config.lang["mensajes"]["bot_iniciado"][config.pred_lang]}-----')

def build_application():
    return (
        ApplicationBuilder()
        .token(config.telegram_token)
        .concurrent_updates(True)
        .http_version("1.1")
        .get_updates_http_version("1.1")
        .rate_limiter(AIORateLimiter(max_retries=5))
        .post_init(post_init)
        .build()
    )
def get_user_filter():
    usernames = []
    user_ids = []
    for user in config.user_whitelist:
        user = user.strip()
        if user.isnumeric():
            user_ids.append(int(user))
        else:
            usernames.append(user)
    return filters.User(username=usernames) | filters.User(user_id=user_ids) if config.user_whitelist else filters.ALL
def get_chat_filter():
    chat_ids = []
    for chat in config.chat_whitelist:
        chat = chat.strip()
        if chat[0] == "-" and chat[1:].isnumeric():
            chat_ids.append(int(chat))
    return filters.Chat(chat_id=chat_ids) if config.chat_whitelist else filters.ALL

def add_handlers(application, user_filter, chat_filter):
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & (user_filter | chat_filter), message.wrapper))
    if config.switch_voice == True:
        application.add_handler(MessageHandler(filters.AUDIO & (user_filter | chat_filter), voice.wrapper))
        application.add_handler(MessageHandler(filters.VOICE & (user_filter | chat_filter), voice.wrapper))
    if config.switch_ocr == True:
        application.add_handler(MessageHandler(filters.PHOTO & (user_filter | chat_filter), ocr_image.wrapper))
    if config.switch_docs == True:
        docfilter = (filters.Document.FileExtension("pdf") | filters.Document.FileExtension("lrc") | filters.Document.FileExtension("json"))
        application.add_handler(MessageHandler(docfilter & (user_filter | chat_filter), document.wrapper))
        application.add_handler(MessageHandler(filters.Document.Category('text/') & (user_filter | chat_filter), document.wrapper))

    application.add_handler(CommandHandler("start", start.handle, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("help", help.handle, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("helpgroupchat", help.group, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("retry", retry.handle, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("new", new.handle, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("cancel", cancel.handle, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("chat_mode", chat_mode.handle, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("model", model.handle, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("status", status.handle, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("reset", reset.handle, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("api", api.handle, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("props", props.handle, filters=(user_filter | chat_filter)))

    if config.switch_imgs == True:
        application.add_handler(CommandHandler("img", img.wrapper, filters=(user_filter | chat_filter)))
        application.add_handler(CallbackQueryHandler(img.callback, pattern="^imgdownload"))
        application.add_handler(CommandHandler("istyle", istyle.imagine, filters=(user_filter | chat_filter)))
        application.add_handler(CommandHandler("iratio", iratio.imagine, filters=(user_filter | chat_filter)))
    if config.switch_search == True:
        application.add_handler(CommandHandler("search", search.wrapper, filters=(user_filter | chat_filter)))
    application.add_handler(CommandHandler("lang", lang.handle, filters=(user_filter | chat_filter)))
    application.add_handler(CallbackQueryHandler(lang.set, pattern="^set_lang"))

    application.add_handler(CallbackQueryHandler(timeout.answer, pattern="^new_dialog"))
    application.add_handler(CallbackQueryHandler(message.actions, pattern="^action"))
    mcbc = "^get_menu"
    application.add_handler(CallbackQueryHandler(chat_mode.callback, pattern=mcbc))
    application.add_handler(CallbackQueryHandler(chat_mode.set, pattern="^set_chat_mode"))
    application.add_handler(CallbackQueryHandler(props.callback, pattern=mcbc))
    application.add_handler(CallbackQueryHandler(props.set, pattern="^set_props"))
    application.add_handler(CallbackQueryHandler(model.callback, pattern=mcbc))
    application.add_handler(CallbackQueryHandler(model.set, pattern="^set_model"))
    application.add_handler(CallbackQueryHandler(api.callback, pattern=mcbc))
    application.add_handler(CallbackQueryHandler(api.set, pattern="^set_api"))
    application.add_handler(CallbackQueryHandler(img.options_callback, pattern=mcbc))
    application.add_handler(CallbackQueryHandler(img.options_set, pattern="^set_image_api"))
    application.add_handler(CallbackQueryHandler(imagine.set, pattern="^set_imaginepy"))

def run_bot() -> None:
    try:
        application = build_application()
        user_filter = get_user_filter()
        chat_filter = get_chat_filter()
        add_handlers(application, user_filter, chat_filter)
        application.add_error_handler(error)
        application.run_polling()
    except telegram.error.TimedOut: logger.error('Timed out')
    except telegram.error.BadRequest as e:
        if "Query is too old" in str(e): logger.error('QueryTimeout')
        if "Replied message not found" in str(e): logger.error('No message to reply')
    except Exception as e: logger.error(f'{__name__}: <run_bot> {config.lang["errores"]["error"][config.pred_lang]}: {e}.')
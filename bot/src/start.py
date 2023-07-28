from bot.src.utils.constants import logger

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
api, img, lang, status, reset, search, props, istyle, iratio, imodel)
from .handlers.callbacks import stablehorde
from .tasks import apis_chat, apis_image, cache, apis_check_idler
from .utils import config
from .utils.proxies import bb, asyncio

async def post_init(application: Application):
    bb(cache.task())
    if config.disable_apis_checkers != True:
        bb(apis_check_idler.task())
        bb(apis_chat.task())
        bb(apis_image.task())
    else:
        logger.info("🚫🔌🌐🔄")
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
    logger.info(f'-----{config.lang[config.pred_lang]["mensajes"]["bot_iniciado"]}-----')

def build_application():
    return (
        ApplicationBuilder()
        .token(config.telegram_token)
        .concurrent_updates(True)
        #some tweaks for slow networks
        .connect_timeout(20.0)
        .read_timeout(15.0)
        .write_timeout(25.0)
        .get_updates_read_timeout(15.0)
        .get_updates_write_timeout(25.0)
        .pool_timeout(9.0)
        #
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

async def add_handlers_parallel(application, user_filter, chat_filter):
    mcbc = "^get_menu"
    
    add_this = [
    MessageHandler(filters.TEXT & ~filters.COMMAND & (user_filter | chat_filter), message.wrapper),
    CommandHandler("start", start.handle, filters=(user_filter | chat_filter)),
    CommandHandler("help", help.handle, filters=(user_filter | chat_filter)),
    CommandHandler("helpgroupchat", help.group, filters=(user_filter | chat_filter)),
    CommandHandler("retry", retry.handle, filters=(user_filter | chat_filter)),
    CommandHandler("new", new.handle, filters=(user_filter | chat_filter)),
    CommandHandler("cancel", cancel.handle, filters=(user_filter | chat_filter)),
    CommandHandler("chat_mode", chat_mode.handle, filters=(user_filter | chat_filter)),
    CommandHandler("model", model.handle, filters=(user_filter | chat_filter)),
    CommandHandler("status", status.handle, filters=(user_filter | chat_filter)),
    CommandHandler("reset", reset.handle, filters=(user_filter | chat_filter)),
    CommandHandler("api", api.handle, filters=(user_filter | chat_filter)),
    CommandHandler("props", props.handle, filters=(user_filter | chat_filter)),
    CommandHandler("lang", lang.handle, filters=(user_filter | chat_filter)),
    CallbackQueryHandler(lang.set, pattern="^set_lang"),
    CallbackQueryHandler(timeout.answer, pattern="^new_dialog"),
    CallbackQueryHandler(message.actions, pattern="^action"),
    CallbackQueryHandler(chat_mode.callback, pattern=mcbc),
    CallbackQueryHandler(chat_mode.set, pattern="^set_chat_mode"),
    CallbackQueryHandler(props.callback, pattern=mcbc),
    CallbackQueryHandler(props.set, pattern="^set_props"),
    CallbackQueryHandler(model.callback, pattern=mcbc),
    CallbackQueryHandler(model.set, pattern="^set_model"),
    CallbackQueryHandler(api.callback, pattern=mcbc),
    CallbackQueryHandler(api.set, pattern="^set_api"),
    CallbackQueryHandler(img.options_callback, pattern=mcbc),
    CallbackQueryHandler(img.options_set, pattern="^set_image_api"),
    CallbackQueryHandler(img.options_set, pattern="^set_image_api_styles"),
    CallbackQueryHandler(stablehorde.set, pattern="^set_stablehorde"),
    ]
    
    if config.switch_voice == True:
        add_this.append(MessageHandler(filters.AUDIO & (user_filter | chat_filter), voice.wrapper))
        add_this.append(MessageHandler(filters.VOICE & (user_filter | chat_filter), voice.wrapper))
    if config.switch_ocr == True:
        add_this.append(MessageHandler(filters.PHOTO & (user_filter | chat_filter), ocr_image.wrapper))
    if config.switch_docs == True:
        docfilter = (filters.Document.FileExtension("pdf") | filters.Document.FileExtension("lrc") | filters.Document.FileExtension("json"))
        add_this.append(MessageHandler(docfilter & (user_filter | chat_filter), document.wrapper))
        add_this.append(MessageHandler(filters.Document.Category('text/') & (user_filter | chat_filter), document.wrapper))
    if config.switch_imgs == True:
        add_this.append(CommandHandler("img", img.wrapper, filters=(user_filter | chat_filter)))
        add_this.append(CommandHandler("istyle", istyle.image_style, filters=(user_filter | chat_filter)))
        add_this.append(CallbackQueryHandler(img.callback, pattern="^imgdownload"))
        if "stablehorde" in apis_image.img_vivas:
            add_this.append(CommandHandler("imodel", imodel.stablehorde, filters=(user_filter | chat_filter)))
    if config.switch_search == True:
        add_this.append(CommandHandler("search", search.wrapper, filters=(user_filter | chat_filter)))
    
    
    add_handler_tasks = [
        add_async_handler(application, handler) for handler in add_this
    ]

    await asyncio.gather(*add_handler_tasks)
    
async def add_async_handler(application, handler):
    application.add_handler(handler)
    
import concurrent.futures

def run_parallel_tasks():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Ejecutar las tres funciones en paralelo
        application_future = executor.submit(build_application)
        user_filter_future = executor.submit(get_user_filter)
        chat_filter_future = executor.submit(get_chat_filter)

        # Obtener los resultados de las funciones
        application = application_future.result()
        user_filter = user_filter_future.result()
        chat_filter = chat_filter_future.result()

    return application, user_filter, chat_filter

def run_bot() -> None:
    application, user_filter, chat_filter = run_parallel_tasks()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(add_handlers_parallel(application, user_filter, chat_filter))
    application.add_error_handler(error)
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(application.run_polling())

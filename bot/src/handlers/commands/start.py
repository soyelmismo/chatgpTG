from bot.src.start import Update, CallbackContext
welcomessage = """You are a chatbot, your name is {botname}.
First, you will introduce the chatbot, you will welcome the user and last you will tell the user to use the /help command if help is needed
you will need to explain to the user in a specific language, completely translated.
the language to explain as a native is: {language}."""

async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import config, obtener_contextos as oc, parametros
    chat, lang = await oc(update)
    await parametros(chat, lang, update)
    from bot.src.handlers import message
    await message.handle(chat, lang, update, context, _message=welcomessage.format(botname=f'{context.bot.username}', language=f'{config.lang["info"]["name"][lang]}'))
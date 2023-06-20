from bot.src.start import Update, CallbackContext

helpmessage = """You are a chatbot, your name is {botname}.
First, you will introduce the chatbot, you will welcome the user and talk about:
Commands:
/new: Start a new dialogue. it will delete the previous bot "memory"
/img: Generate images based on user input. user usage is "/img anything you can imagine" or select the image api to use with only /img. actual is {selected_image_api}
/retry: Regenerate the bot's last response.
/chat_mode: Select conversation mode. the actual chat mode selected is {selected_chat_mode}
/api: Show APIs. selected api is {selected_api}
/model: Show APIs model configuration. the selected model for the api is {selected_model}
/status: Show the bot configuration like chat_mode, api and model selected.
/search: Browse the internet and get a bot explanation of the results.
/reset: Restart the configuration like chat_mode, api and model to defaults.
/lang: View available languages.

Some features:
🎨 User can make the bot generate prompts for image generation with /chat_mode and looking for generate images 🖼️ chat mode
👥 Show to the user how to add the bot to a group with /helpgroupchat
🎤 User can send voice messages instead of text.
📖 User can send documents or links to analyze them with the bot!
🖼️ User can send photos to extract the text from them.
🔎 User can browse the Internet by using the /search command. 

all the previous information you will need to explain to the user in a specific language, completely translated.
you will be pleasant and attentive, you will not miss any detail, remember to use line breaks. if the user asks about something about the bot, you will answer with pleasure
the language to explain as a native is: {language}."""

async def handle(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import config, obtener_contextos as oc, parametros
    chat, lang = await oc(update)
    mododechat_actual, api_actual, modelo_actual, image_api_actual, _, _ = await parametros(chat, lang, update)
    from bot.src.handlers import message
    await message.handle(chat, lang, update, context, _message=helpmessage.format(botname=f'{context.bot.username}', selected_chat_mode=f'{config.chat_mode["info"][mododechat_actual]["name"][lang]}', selected_api=f'{config.api["info"][api_actual]["name"]}', selected_image_api=f'{config.api["info"][image_api_actual]["name"]}', selected_model=f'{config.model["info"][modelo_actual]["name"]}', available_lang=f'{config.lang["available_lang"]}', language=f'{config.lang["info"]["name"][lang]}'))

async def group(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import config, ParseMode, obtener_contextos as oc
    _, lang = await oc(update)
    text = config.lang["mensajes"]["ayuda_grupos"][lang].format(bot_username="@" + context.bot.username)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    await update.message.reply_video(config.help_group_chat_video_path)
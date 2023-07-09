from bot.src.start import Update, CallbackContext
from bot.src.utils.constants import constant_db_tokens
async def handle(update: Update, context: CallbackContext, paraprops=None):
    try:
        from bot.src.utils.proxies import obtener_contextos as oc, parametros, db, config
        chat, lang =  await oc(update)
        mododechat_actual, api_actual, modelo_actual, checked_image_api, checked_imaginepy_styles, _, checked_imaginepy_models = await parametros(chat, lang, update)
        tokens_actual = await db.get_dialog_attribute(chat, f'{constant_db_tokens}')

        api=config.lang[lang]["metagen"]["api"]
        nombreapi=config.api["info"][api_actual]["name"]
        apimagen=config.lang[lang]["metagen"]["image_api"]
        apimagenestilo=config.lang[lang]["metagen"]["imaginepy_styles"]
        nombreapimagen=config.api["info"][checked_image_api]["name"]
        imaginestyle=config.lang[lang]["metagen"]["imaginepy_actual_style"]
        imaginemodel=config.lang[lang]["metagen"]["imaginepy_actual_model"]
        modelo=config.lang[lang]["metagen"]["modelo"]
        nombremodelo=config.model["info"][modelo_actual]["name"]
        tokensmax=config.lang[lang]["metagen"]["tokensmax"]
        modeltokens=config.model["info"][modelo_actual]["max_tokens"]
        if config.api["info"][api_actual].get("api_max_tokens"):
            modeltokens = config.api["info"][api_actual]["api_max_tokens"]
        chatmode=config.lang[lang]["metagen"]["chatmode"]
        nombrechatmode=config.chat_mode["info"][mododechat_actual]["name"][lang]
        tokens=config.lang[lang]["metagen"]["tokens"]
        textoprimer="""🔌 {api}: {nombreapi}\n🧠 {modelo}: {nombremodelo}\n💬 {chatmode}: {nombrechatmode}\n💰 {tokens}: {tokens_actual} / {modeltokens}\n\n🌅 {apimagen}: {apimageactual}\n🎨 {apimagenestilo}: {imagineactual}"""
        if checked_image_api =="imaginepy": textoprimer += "\n{imaginestyle}: {imagineactual}\n{imaginemodel}: {checked_imaginepy_models}"
        text = f'{textoprimer.format(imaginemodel=imaginemodel, checked_imaginepy_models=checked_imaginepy_models, api=api, nombreapi=nombreapi,modelo=modelo,nombremodelo=nombremodelo, tokensmax=tokensmax,modeltokens=modeltokens,chatmode=chatmode, nombrechatmode=nombrechatmode,tokens=tokens, tokens_actual=tokens_actual,apimagen=apimagen, apimageactual=nombreapimagen,apimagenestilo=apimagenestilo,imaginestyle=imaginestyle, imagineactual=checked_imaginepy_styles)}'
    
        if paraprops: return text
        await update.effective_chat.send_message(text)
    except Exception as e:
        raise ValueError(f'<status handle> {e}>')

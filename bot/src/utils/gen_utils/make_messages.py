from bot.src.utils import config
from bot.src.utils.constants import continue_key

def append_resources_messages(self, messages, dialog_messages):
    documento_texts = []
    url_texts = []
    search_texts = []
    for dialog_message in dialog_messages:
        documento, url, search = process_resources_message(dialog_message)
        documento_texts, url_texts, search_texts = append_resources_texts(documento, url, search, documento_texts, url_texts, search_texts, lang=self.lang)
    if documento_texts or url_texts or search_texts:
        messages.append({
            "role": "system",
            "content": f'{str(documento_texts) if documento_texts else ""}\n{str(url_texts) if url_texts else ""}\n{str(search_texts) if search_texts else ""}\n: {config.lang[self.lang]["metagen"]["contexto"]}'
        })
    return messages
def process_resources_message(dialog_message):
    documento = dialog_message.get("documento", "")
    url = dialog_message.get("url", "")
    search = dialog_message.get("search", "")
    return documento, url, search
def append_resources_texts(documento, url, search, documento_texts, url_texts, search_texts, lang):
    if len(documento) > 1:
        documento_texts.append(f"'{config.lang[lang]['metagen']['documentos']}': {documento}")
    if len(url) > 1:
        url_texts.append(f"'{config.lang[lang]['metagen']['paginas']}': {url}")
    if len(search) > 1:
        search_texts.append(f"'{config.lang[lang]['metagen']['busquedaweb']}': {search}")
    return documento_texts, url_texts, search_texts

def append_user_bot_messages(messages, dialog_messages):
    for dialog_message in dialog_messages:
        user = dialog_message.get("user", "")
        bot = dialog_message.get("bot", "")
        if len(user) >= 2:
            messages.append({"role": "user", "content": user})
        if len(bot) >= 2:
            messages.append({"role": "assistant", "content": bot})
    return messages

def append_chat_mode(self, chat_mode, messages):
    if chat_mode == "imagen":
        messages.append({"role": "system", "content": f'{config.chat_mode["info"][chat_mode]["prompt_start"]}'})
    elif chat_mode != "nada":
        language = config.lang[self.lang]["info"]["name"]
        especificacionlang = config.especificacionlang.format(language=language)
        prompter = config.chat_mode["info"][chat_mode]["prompt_start"].format(language=language)
        injectprompt = """{especificarlang}\n\n{elprompt}\n\n{especificarlang}\n\n"""
        messages.append({"role": "system", "content": injectprompt.format(especificarlang=especificacionlang, elprompt=prompter)})
    return messages

def continue_or_append_latest_message(_message, messages):
    if _message == continue_key:
        _message = ""
        last_assistant_message_index = next((index for index, message in reversed(list(enumerate(messages))) if message["role"] == "assistant"), -1)
        if last_assistant_message_index != -1:
            content = messages[last_assistant_message_index]["content"]
            if content.endswith("."): messages[last_assistant_message_index]["content"] = content[:-2]
    else:
        messages.append({"role": "user", "content": _message})
    return messages

def append_functions(messages, dialog_messages):
    for dialog_message in dialog_messages:
        messages.append({
            "role": 'function',
            "name": dialog_message.get('function', ''),
            "content": dialog_message.get('content', ''),
        })
    return messages

async def handle(self, _message="", dialog_messages=[], chat_mode="nada"):
    try:
        messages = []
        messages = append_resources_messages(self, messages, dialog_messages)
        messages = append_functions(messages, dialog_messages)
        messages = append_user_bot_messages(messages, dialog_messages)
        messages = append_chat_mode(self, chat_mode, messages)
        messages = continue_or_append_latest_message(_message, messages)
        messages = [message for message in messages if message["content"]]
        return messages
    except Exception as e:
        e = f'_generate_prompt_messages: {e}'
        raise ValueError(e)

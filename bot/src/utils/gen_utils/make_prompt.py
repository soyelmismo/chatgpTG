from bot.src.utils import config
from bot.src.utils.constants import continue_key

def get_texts(dialog_messages, key):
    texts = [dialog_message.get(key, "").strip() for dialog_message in dialog_messages if len(dialog_message.get(key, "")) >= 5]
    return "\n".join(texts) if texts else ""

def get_prompt_lines(dialog_messages, chat_mode, lang):
    prompt_lines = []
    for dialog_message in dialog_messages:
        user_text = dialog_message.get("user", "").strip()
        if user_text:
            prompt_lines.append(f'{config.lang["metagen"]["usuario"][lang]}: {user_text}\n')
        bot_text = dialog_message.get("bot", "").strip()
        if bot_text:
            prompt_lines.append(f'{config.chat_mode["info"][chat_mode]["name"][lang]}: {bot_text}\n')
    return "".join(prompt_lines)

def get_injectprompt(language, prompter):
    especificacionlang = config.lang["metagen"]["especificacionlang"].format(language=language)
    injectprompt = """{especificarlang}\n\n{elprompt}\n\n{especificarlang}\n\n"""
    return injectprompt.format(especificarlang=especificacionlang, elprompt=prompter)
    
async def handle(self, _message="", dialog_messages=[], chat_mode="nada"):
    try:
        prompt = ""
        documento_texts = ""
        url_texts = ""
        search_texts = ""
        documento_texts = get_texts(dialog_messages, "documento")
        url_texts = get_texts(dialog_messages, "url")
        search_texts = get_texts(dialog_messages, "search")
        if documento_texts or url_texts or search_texts:
            prompt += f'{config.lang["metagen"]["documentos"][self.lang]}: {documento_texts}\n\n{config.lang["metagen"]["urls"][self.lang]}: {url_texts}\n\n{config.lang["metagen"]["busquedaweb"][self.lang]}: {search_texts}\n\n{config.lang["metagen"]["mensaje"][self.lang]}: [{prompt}][{config.lang["metagen"]["contexto"][self.lang]}]'
        prompt += f'{config.lang["metagen"]["log"][self.lang]}:\n'
        prompt += get_prompt_lines(dialog_messages, chat_mode, lang=self.lang)
        if chat_mode == "imagen":
            prompt += f'{config.chat_mode["info"][chat_mode]["prompt_start"]}'
        elif chat_mode != "nada":
            language = config.lang["info"]["name"][self.lang]
            prompter = config.chat_mode["info"][chat_mode]["prompt_start"].format(language=language)
            prompt += get_injectprompt(language, prompter)
        if _message == continue_key:
            _message = ""
            if prompt.endswith(".") or prompt.endswith("?"):
                prompt = prompt[:-3]
        else:
            prompt += f'{config.lang["metagen"]["usuario"][self.lang]}: {_message}'
            if chat_mode != "nada": prompt += f'{config.chat_mode["info"][chat_mode]["name"][self.lang]}:'
        return prompt
    except Exception as e:
        e = f'_generate_prompt: {e}'
        raise Exception(e)
async def handle(self, _message="", dialog_messages=[], chat_mode="nada"):
    from bot.src.utils import config

    try:
        messages = []
        documento_texts = []
        url_texts = []
        search_texts=[]
        for dialog_message in dialog_messages:
            documento = dialog_message.get("documento", "")
            url = dialog_message.get("url", "")
            search = dialog_message.get("search", "")
            if len(documento) > 1:
                documento_texts.append(f"'{config.lang['metagen']['documentos'][self.lang]}': {documento}")
            if len(url) > 1:
                url_texts.append(f"'{config.lang['metagen']['paginas'][self.lang]}': {url}")
            if len(search) > 1:
                search_texts.append(f"'{config.lang['metagen']['busquedaweb'][self.lang]}': {search}")
        if documento_texts or url_texts or search_texts:
            messages.append({
                "role": "system",
                "content": f'{str(documento_texts) if documento_texts else ""}\n{str(url_texts) if url_texts else ""}\n{str(search_texts) if search_texts else ""}\n: {config.lang["metagen"]["contexto"][self.lang]}'
            })
        for dialog_message in dialog_messages:
            user = dialog_message.get("user", "")
            bot = dialog_message.get("bot", "")
            if len(user) >= 2:
                messages.append({"role": "user", "content": dialog_message.get("user", "")})
            if len(bot) >= 2:
                messages.append({"role": "assistant", "content": dialog_message.get("bot", "")})
        if chat_mode == "nada":
            pass
        else:
            messages.append({"role": "system", "content": f'{config.chat_mode["info"][chat_mode]["name"][self.lang]}: {config.chat_mode["info"][chat_mode]["prompt_start"][self.lang]}'})
        if _message == "Renounce€Countless€Unrivaled2€Banter":
            _message = ""
            # Encuentra el último mensaje de 'assistant'
            last_assistant_message_index = -1
            for index, message in reversed(list(enumerate(messages))):
                if message["role"] == "assistant":
                    last_assistant_message_index = index
                    break
            # Reemplaza el último punto con una coma en el último mensaje de 'assistant'
            if last_assistant_message_index != -1:
                content = messages[last_assistant_message_index]["content"]
                if content.endswith("."):
                    messages[last_assistant_message_index]["content"] = content[:-2]
        else:
            messages.append({"role": "user", "content": _message})
        messages = [message for message in messages if message["content"]]
        return messages
    except Exception as e:
        e = f'_generate_prompt_messages: {e}'
        raise Exception(e)
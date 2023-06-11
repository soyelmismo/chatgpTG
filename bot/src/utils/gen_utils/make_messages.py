async def handle(self, _message="", dialog_messages=[], chat_mode="nada"):
    from bot.src.utils import config

    try:
        prompt = config.chat_mode["info"][chat_mode]["prompt_start"][self.lang]
        messages = [{"role": "system", "content": f'{prompt}'}]
        documento_texts = []
        url_texts = []
        for dialog_message in dialog_messages:
            documento_texts.append(f'{dialog_message.get("documento", "")}\n')
            url_texts.append(f'{dialog_message.get("url", "")}\n')
        if documento_texts or url_texts:
            messages = [{"role": "system", "content": f'{config.lang["metagen"]["documentos"][self.lang]}: [{documento_texts}]\n\n{config.lang["metagen"]["urls"][self.lang]}: [{url_texts}]\n\n{config.lang["metagen"]["mensaje"][self.lang]}: [{prompt}][{config.lang["metagen"]["contexto"][self.lang]}]'}]
        else:
            # Mantener el mensaje system original 
            messages = [{"role": "system", "content": f'{prompt}'}]
        for dialog_message in dialog_messages:
            messages.append({"role": "user", "content": dialog_message.get("user", "")})
            messages.append({"role": "assistant", "content": dialog_message.get("bot", "")})
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
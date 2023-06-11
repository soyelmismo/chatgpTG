async def handle(self, _message="", dialog_messages=[], chat_mode="nada"):
    from bot.src.utils import config

    try:
        prompt = f'{config.chat_mode["info"][chat_mode]["prompt_start"][self.lang]}'
        prompt += "\n\n"
        # add chat context
        prompt += f'{config.lang["metagen"]["log"][self.lang]}:\n'
        documento_texts=[]
        url_texts=[]
        for dialog_message in dialog_messages:
            documento_texts.append(dialog_message.get("documento", "").strip())
            url_texts.append(dialog_message.get("url", "").strip())
        documento_texts = "\n".join(documento_texts)
        url_texts = "\n".join(url_texts)
        if len(documento_texts) > 0 or len(url_texts) > 0:
            prompt += f'{config.lang["metagen"]["documentos"][self.lang]}: [{documento_texts}]\n\n{config.lang["metagen"]["urls"][self.lang]}: [{url_texts}]\n\n{config.lang["metagen"]["mensaje"][self.lang]}: [{prompt}][{config.lang["metagen"]["contexto"][self.lang]}]'
        
        prompt_lines = []

        for dialog_message in dialog_messages:
            user_text = dialog_message.get("user", "").strip()
            if user_text:
                prompt_lines.append(f'{config.lang["metagen"]["usuario"][self.lang]}: {user_text}\n')
        
            bot_text = dialog_message.get("bot", "").strip()
            if bot_text:
                prompt_lines.append(f'{config.chat_mode["info"][chat_mode]["name"][self.lang]}: {bot_text}\n')
        
        prompt += "".join(prompt_lines)
        
        if _message == "Renounce€Countless€Unrivaled2€Banter":
            _message = ""
            #prompt+= "\nresumeLongGeneration\n:"
            if prompt.endswith(".") or prompt.endswith("?"):
                prompt = prompt[:-3]
        else:
            # current message
            prompt += f'{config.lang["metagen"]["usuario"][self.lang]}: {_message}\n'
            prompt += f'{config.chat_mode["info"][chat_mode]["name"][self.lang]}:'
        return prompt
    except Exception as e:
        e = f'_generate_prompt: {e}'
        raise Exception(e)
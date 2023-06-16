async def handle(self, _message="", dialog_messages=[], chat_mode="nada"):
    from bot.src.utils import config

    try:
        prompt = ""
        # add chat context
        documento_texts=[]
        url_texts=[]
        search_texts=[]
        for dialog_message in dialog_messages:
            documento = dialog_message.get("documento", "")
            url = dialog_message.get("url", "")
            search = dialog_message.get("search", "")
            if len(documento) >= 5:
                documento_texts.append(dialog_message.get("documento", "").strip())
            if len(url) >= 5:
                url_texts.append(dialog_message.get("url", "").strip())
            if len(search) >= 5:
                search_texts.append(dialog_message.get("search", "").strip())
        documento_texts = "\n".join(documento_texts) if documento_texts else ""
        url_texts = "\n".join(url_texts) if url_texts else ""
        search_texts = "\n".join(search_texts) if search_texts else ""
        if documento_texts or url_texts or search_texts:
            prompt += f'{config.lang["metagen"]["documentos"][self.lang]}: {documento_texts}\n\n{config.lang["metagen"]["urls"][self.lang]}: {url_texts}\n\n{config.lang["metagen"]["busquedaweb"][self.lang]}: {search_texts}\n\n{config.lang["metagen"]["mensaje"][self.lang]}: [{prompt}][{config.lang["metagen"]["contexto"][self.lang]}]'
        prompt += f'{config.lang["metagen"]["log"][self.lang]}:\n'
        prompt_lines = []
        for dialog_message in dialog_messages:
            user_text = dialog_message.get("user", "").strip()
            if user_text:
                prompt_lines.append(f'{config.lang["metagen"]["usuario"][self.lang]}: {user_text}\n')
            bot_text = dialog_message.get("bot", "").strip()
            if bot_text:
                prompt_lines.append(f'{config.chat_mode["info"][chat_mode]["name"][self.lang]}: {bot_text}\n')
        prompt += "".join(prompt_lines)
        if chat_mode == "nada":
            pass
        elif chat_mode == "imagen":
            prompt += f'{config.chat_mode["info"][chat_mode]["prompt_start"]}'
        else:
            language = config.lang["info"]["name"][self.lang]
            especificacionlang = config.lang["metagen"]["especificacionlang"].format(language=language)
            prompter = config.chat_mode["info"][chat_mode]["prompt_start"].format(language=language)
            injectprompt = """{especificarlang}\n\n{elprompt}\n\n{especificarlang}\n\n"""
            prompt += injectprompt.format(especificarlang=especificacionlang, elprompt=prompter)
        if _message == "Renounce€Countless€Unrivaled2€Banter":
            _message = ""
            #prompt+= "\nresumeLongGeneration\n:"
            if prompt.endswith(".") or prompt.endswith("?"):
                prompt = prompt[:-3]
        else:
            # current message
            prompt += f'{config.lang["metagen"]["usuario"][self.lang]}: {_message}'
            if chat_mode == "nada":
                pass
            else:
                prompt += f'{config.chat_mode["info"][chat_mode]["name"][self.lang]}:'
        return prompt
    except Exception as e:
        e = f'_generate_prompt: {e}'
        raise Exception(e)
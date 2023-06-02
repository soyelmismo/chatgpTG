import config
import database
import openai
import random

db = database.Database()
   
class ChatGPT:
    def __init__(self, chat, model="gpt-3.5-turbo"):
        self.chat = chat
        self.model = model
        assert model in config.model["available_model"], f"Unknown model: {model}"
        self.api = db.get_chat_attribute(self.chat, "current_api")
        self.diccionario = {}

    async def send_message(self, _message, lang="es", dialog_messages=[], chat_mode="assistant"):
        if self.model not in config.model["available_model"]:
            raise LookupError(f'{config.lang["errores"]["utils_modelo_desconocido"][lang]}: {self.model}')
        self.diccionario.clear()
        self.diccionario.update(config.completion_options)
        answer = None
        while answer is None:
            try:
                answer = ""
                messages = self._generate_prompt_messages(_message, dialog_messages, chat_mode, lang)
                if self.api == "chatbase":
                    from apis.opengpt import chatbase
                    r = chatbase.GetAnswer(messages=messages, model=self.model)
                    answer = r
                    if "API rate limit exceeded" in answer:
                        raise RuntimeError(config.lang["errores"]["utils_chatbase_limit"][lang])
                    yield "not_finished", answer
                elif self.api == "g4f":
                    from apis.gpt4free import g4f
                    provider_name = config.model['info'][self.model]['name']
                    provider = getattr(g4f.Providers, provider_name)
                    r = g4f.ChatCompletion.create(provider=provider, model='gpt-3.5-turbo', messages=messages, stream=True)
                    for chunk in r:
                        answer += chunk
                        yield "not_finished", answer
                elif self.api == "you":
                    from apis.gpt4free.foraneo import you
                    r = you.Completion.create(
                        prompt=messages,
                        chat=dialog_messages,
                        detailed=False,
                        include_links=True)
                    r = dict(r)
                    answer += r["text"].encode('utf-16', 'surrogatepass').decode('utf-16')  # Aquí aplicamos la codificación y decodificación
                    if "Unable to fetch the response, Please try again." in answer:
                        raise RuntimeError(answer)
                    if len(r["links"]) >= 1:
                        answer += "\n\nLinks: \n"
                        for link in r["links"]:
                                link_name = link['name']
                                answer += f"\n- [{link_name}]({link['url']})"
                    yield "not_finished", answer
                else:
                    api_info = config.api["info"].get(self.api, {})
                    openai.api_key = str(api_info.get("key", ""))
                    openai.api_base=str(config.api["info"][self.api].get("url"))
                    if self.model not in config.model["text_completions"]:
                        self.diccionario["messages"] = messages
                        self.diccionario["model"] = self.model
                        fn = openai.ChatCompletion.acreate
                    else:
                        prompt = self._generate_prompt(_message, dialog_messages, chat_mode, lang)
                        self.diccionario["prompt"] = prompt
                        self.diccionario["model"] = self.model
                        fn = openai.Completion.acreate
                    r = await fn(stream=True, **self.diccionario)
                    async for r_item in r:
                        if self.model not in config.model["text_completions"]:
                            delta = r_item.choices[0].delta
                            if "content" in delta:
                                answer += delta.content
                        else:
                            answer += r_item.choices[0].text
                        yield "not_finished", answer
                answer = self._postprocess_answer(answer)
            except openai.error.InvalidRequestError as e:  # too many tokens
                if len(dialog_messages) == 0:
                    raise IndexError(f'{config.lang["errores"]["utils_dialog_messages_0"][lang]} [{self.api}]: {e}') from e
                # forget first message in dialog_messages
                dialog_messages = dialog_messages[1:]
            except Exception as e:
                raise ValueError(f'[{self.api}]: {e}')
        yield "finished", answer

    def _generate_prompt(self, _message, dialog_messages, chat_mode, lang):
        prompt = f'{config.chat_mode["info"][chat_mode]["prompt_start"][lang]}'
        prompt += "\n\n"

        # add chat context
        if len(dialog_messages) > 0:
            prompt += f'{config.lang["metagen"]["log"][lang]}:\n'
            for dialog_message in dialog_messages:
                if "documento" in dialog_message:
                    prompt += f'{config.lang["metagen"]["documentos"][lang]}: [{dialog_message["documento"]}]'
                if "url" in dialog_message:
                    prompt += f'{config.lang["metagen"]["urls"][lang]}: [{dialog_message["url"]}]'
                if "user" in dialog_message:
                    prompt += f'{config.lang["metagen"]["usuario"][lang]}: {dialog_message["user"]}\n'
                if "bot" in dialog_message:
                    prompt += f'{config.lang["metagen"]["robot"][lang]}: {dialog_message["bot"]}\n'

        # current message
        prompt += f'{config.lang["metagen"]["usuario"][lang]}: {_message}\n'
        prompt += f'{config.lang["metagen"]["robot"][lang]}:'

        return prompt

    def _generate_prompt_messages(self, _message, dialog_messages, chat_mode, lang):
        prompt = config.chat_mode["info"][chat_mode]["prompt_start"][lang]
        messages = [{"role": "system", "content": f'{prompt}'}]
        documento_texts = []
        url_texts = []
        for dialog_message in dialog_messages:
            if "documento" in dialog_message:
                documento_texts.append(f'{dialog_message["documento"]}\n')
            if "url" in dialog_message:
                url_texts.append(f'{dialog_message["url"]}\n')
        if documento_texts or url_texts:
           messages = [{"role": "system", "content": f'{config.lang["metagen"]["documentos"][lang]}: [{documento_texts}]\n\n{config.lang["metagen"]["urls"][lang]}: [{url_texts}]\n\n{config.lang["metagen"]["mensaje"][lang]}: [{prompt}][{config.lang["metagen"]["contexto"][lang]}]'}]
        else:
           # Mantener el mensaje system original 
           messages = [{"role": "system", "content": f'{prompt}'}]
        for dialog_message in dialog_messages:
            if "user" in dialog_message:
                messages.append({"role": "user", "content": dialog_message["user"]})
            if "bot" in dialog_message:
                messages.append({"role": "assistant", "content": dialog_message["bot"]})
        messages.append({"role": "user", "content": _message})
        return messages

    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer
    
    async def transcribe_audio(self, audio_file):
        if self.api not in config.api["available_transcript"]:
            index = random.randint(1, len(config.api["available_transcript"]))
            self.api = config.api["available_transcript"][index]
        openai.api_key = config.api["info"][self.api]["key"]
        openai.api_base = config.api["info"][self.api]["url"]
        r = await openai.Audio.atranscribe("whisper-1", audio_file)
        return r["text"]

    async def generate_images(self, prompt):
        if self.api not in config.api["available_imagen"]:
            index = random.randint(1, len(config.api["available_imagen"]))
            self.api = config.api["available_imagen"][index]
        openai.api_key = config.api["info"][self.api]["key"]
        openai.api_base = config.api["info"][self.api]["url"]
        r = await openai.Image.acreate(prompt=prompt, n=config.n_images, size="1024x1024")
        image_urls = [item.url for item in r.data]
        return image_urls

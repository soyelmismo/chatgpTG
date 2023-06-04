import config
import database
import openai
import random

db = database.Database()
   
class ChatGPT:
    def __init__(self, chat, lang="es", model="gpt-3.5-turbo"):
        self.chat = chat
        self.model = model
        self.lang = lang
        self.answer = None
        assert model in config.model["available_model"], f"Unknown model: {model}"
        self.api = None
        self.diccionario = {}
        self.diccionario.clear()
        self.diccionario.update(config.completion_options)

    async def send_message(self, _message, dialog_messages=[], chat_mode="assistant"):
        while self.answer is None:
            try:
                await self._validate_model()
                async for status, self.answer in self._generate_answer(_message, dialog_messages, chat_mode):
                    yield status, self.answer
            except openai.error.InvalidRequestError as e:  # too many tokens
                if len(dialog_messages) == 0:
                    raise IndexError(f'{config.lang["errores"]["utils_dialog_messages_0"][self.lang]} [{self.api}]: {e}') from e
                # forget first message in dialog_messages
                dialog_messages = dialog_messages[1:]
            except Exception as e:
                e = f'send_message: {e}'
                self._handle_exception(e)
        yield "finished", self.answer
    
    async def _validate_model(self):
        try:
            if self.model not in config.model["available_model"]:
                raise LookupError(f'{config.lang["errores"]["utils_modelo_desconocido"][self.lang]}: {self.model}')
        except Exception as e:
            e = f'_validate_model: {e}'
            raise Exception(e)

    async def _generate_answer(self, _message, dialog_messages, chat_mode):
        try:
            async for status, self.answer in self._make_api_request(_message, dialog_messages, chat_mode):
                yield status, self.answer
        except openai.error.InvalidRequestError as e:
            self._handle_invalid_request_error(e, dialog_messages)
        except Exception as e:
            e = f'_generate_answer: {e}'
            raise Exception(e)

    async def _make_api_request(self, _message, dialog_messages, chat_mode):
        try:
            self.answer = ""
            self.api=await db.get_chat_attribute(self.chat, "current_api")
            messages = await self._generate_prompt_messages(_message, dialog_messages, chat_mode)
            if self.api == "chatbase":
                async for status, self.answer in self._get_chatbase_answer(messages):
                    yield status, self.answer
            elif self.api == "g4f":
                async for status, self.answer in self._get_g4f_answer(messages):
                    yield status, self.answer
            elif self.api == "you":
                async for status, self.answer in self._get_you_answer(messages, dialog_messages):
                    yield status, self.answer
            elif self.api == "evagpt4":
                async for status, self.answer in self._get_evagpt4_answer(messages):
                    yield status, self.answer
            else:
                async for status, self.answer in self._get_openai_answer(_message, messages, dialog_messages, chat_mode):
                    yield status, self.answer
            self.answer = await self._postprocess_answer()
        except Exception as e:
            e = f'_make_api_request: {e}'
            raise Exception(e)

    async def _handle_invalid_request_error(self, error, dialog_messages):
        try:
            if len(dialog_messages) == 0:
                raise IndexError(f'{config.lang["errores"]["utils_dialog_messages_0"][self.lang]} [{self.api}]: {error}') from error
            dialog_messages = dialog_messages[1:]
        except Exception as e:
            e = f'_handle_invalid_request_error: {e}'
            raise Exception(e)

    def _handle_exception(self, error):
        raise ValueError(f'<{self.api}> {error}')

    async def _get_openai_answer(self, _message, messages, dialog_messages, chat_mode):
        try:
            api_info = config.api["info"].get(self.api, {})
            openai.api_key = str(api_info.get("key", ""))
            openai.api_base=str(config.api["info"][self.api].get("url"))
            if self.model not in config.model["text_completions"]:
                self.diccionario["messages"] = messages
                self.diccionario["model"] = self.model
                fn = openai.ChatCompletion.acreate
            else:
                prompt = await self._generate_prompt(_message, dialog_messages, chat_mode)
                self.diccionario["prompt"] = prompt
                self.diccionario["engine"] = self.model
                fn = openai.Completion.acreate
            r = await fn(stream=True, **self.diccionario)
            async for r_item in r:
                if self.model not in config.model["text_completions"]:
                    delta = r_item.choices[0].delta
                    if "content" in delta:
                        self.answer += delta.content
                else:
                    self.answer += r_item.choices[0].text
                yield "not_finished", self.answer
        except Exception as e:
            e = f'_get_openai_answer: {e}'
            raise Exception(e)

    async def _get_you_answer(self, messages, dialog_messages):
        try:
            from apis.gpt4free.foraneo import you
            r = you.Completion.create(
                prompt=messages,
                chat=dialog_messages,
                detailed=False,
                include_links=False
            )
            for chunk in r.text.encode('utf-16', 'surrogatepass').decode('utf-16'):
                self.answer += chunk
                if "Unable to fetch the response, Please try again." in self.answer:
                    raise RuntimeError(self.answer)
                yield "not_finished", self.answer
        except Exception as e:
            e = f'_get_you_answer: {e}'
            raise Exception(e)
            
    async def _get_chatbase_answer(self, messages):
        try:
            from apis.opengpt import chatbase
            r = chatbase.GetAnswer(messages=messages, model=self.model)
            for chunk in r:
                self.answer += chunk
                if "API rate limit exceeded" in self.answer:
                    raise RuntimeError(config.lang["errores"]["utils_chatbase_limit"][self.lang])
                yield "not_finished", self.answer
        except Exception as e:
            e = f'_get_chatbase_answer: {e}'
            raise Exception(e)
    async def _get_evagpt4_answer(self, messages):
        try:
            from apis.opengpt import evagpt4
            r = evagpt4.Model(model=self.model).ChatCompletion(messages)
            for chunk in r:
                self.answer += chunk
                yield "not_finished", self.answer
        except Exception as e:
            e = f'_get_evagpt4_answer: {e}'
            raise Exception(e)

    async def _get_g4f_answer(self, messages):
        try:
            from apis.gpt4free import g4f
            provider_name = config.model['info'][self.model]['name']
            provider = getattr(g4f.Providers, provider_name)
            r = g4f.ChatCompletion.create(provider=provider, model='gpt-3.5-turbo', messages=messages, stream=True)
            for chunk in r:
                self.answer += chunk
                yield "not_finished", self.answer
        except Exception as e:
            e = f'_get_g4f_answer: {e}'
            raise Exception(e)

    async def _generate_prompt(self, _message, dialog_messages, chat_mode):
        try:
            prompt = f'{config.chat_mode["info"][chat_mode]["prompt_start"][self.lang]}'
            prompt += "\n\n"

            # add chat context
            if len(dialog_messages) > 0:
                prompt += f'{config.lang["metagen"]["log"][self.lang]}:\n'
                for dialog_message in dialog_messages:
                    if "documento" in dialog_message:
                        prompt += f'{config.lang["metagen"]["documentos"][self.lang]}: [{dialog_message["documento"]}]'
                    if "url" in dialog_message:
                        prompt += f'{config.lang["metagen"]["urls"][self.lang]}: [{dialog_message["url"]}]'
                    if "user" in dialog_message:
                        prompt += f'{config.lang["metagen"]["usuario"][self.lang]}: {dialog_message["user"]}\n'
                    if "bot" in dialog_message:
                        prompt += f'{config.lang["metagen"]["robot"][self.lang]}: {dialog_message["bot"]}\n'

            # current message
            prompt += f'{config.lang["metagen"]["usuario"][self.lang]}: {_message}\n'
            prompt += f'{config.lang["metagen"]["robot"][self.lang]}:'

            return prompt
        except Exception as e:
            e = f'_generate_prompt: {e}'
            raise Exception(e)

    async def _generate_prompt_messages(self, _message, dialog_messages, chat_mode):
        try:
            prompt = config.chat_mode["info"][chat_mode]["prompt_start"][self.lang]
            messages = [{"role": "system", "content": f'{prompt}'}]
            documento_texts = []
            url_texts = []
            for dialog_message in dialog_messages:
                if "documento" in dialog_message:
                    documento_texts.append(f'{dialog_message["documento"]}\n')
                if "url" in dialog_message:
                    url_texts.append(f'{dialog_message["url"]}\n')
            if documento_texts or url_texts:
                messages = [{"role": "system", "content": f'{config.lang["metagen"]["documentos"][self.lang]}: [{documento_texts}]\n\n{config.lang["metagen"]["urls"][self.lang]}: [{url_texts}]\n\n{config.lang["metagen"]["mensaje"][self.lang]}: [{prompt}][{config.lang["metagen"]["contexto"][self.lang]}]'}]
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
        except Exception as e:
            e = f'_generate_prompt_messages: {e}'
            raise Exception(e)

    async def _postprocess_answer(self):
        try:
            self.answer = self.answer.strip()
            return self.answer
        except Exception as e:
            e = f'_postprocess_answer: {e}'
            raise Exception(e)

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

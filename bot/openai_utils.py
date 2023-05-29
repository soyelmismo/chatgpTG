import config
import database
import openai
import random

db = database.Database()
   
class ChatGPT:
    def __init__(self, model="gpt-3.5-turbo"):
        assert model in config.model["available_model"], f"Unknown model: {model}"
        self.model = model
        self.diccionario = {}

    async def send_message(self, message, chat_id, dialog_messages=[], chat_mode="assistant"):
        self.diccionario.clear()
        self.diccionario.update(config.completion_options)
        api = db.get_chat_attribute(chat_id, "current_api")
        answer = None
        while answer is None:
            try:
                messages = self._generate_prompt_messages(message, dialog_messages, chat_mode)
                if api == "chatbase":
                    from apis.opengpt import chatbase
                    r = chatbase.GetAnswer(messages=messages, model=self.model)
                elif api == "g4f":
                    from apis.gpt4free import g4f
                    provider_name = config.model['info'][self.model]['name']
                    provider = getattr(g4f.Providers, provider_name)
                    # streamed completion
                    r = g4f.ChatCompletion.create(provider=provider, model='gpt-3.5-turbo', messages=messages, stream=True)
                elif api == "you":
                    from apis.gpt4free.foraneo import you
                    r = you.Completion.create(
                        prompt=messages,
                        chat=dialog_messages,
                        detailed=False,
                        include_links=True)
                    r = dict(r)
                else:
                    if (self.model in config.model["available_model"]):
                        api_info = config.api["info"].get(api, {})
                        openai.api_key = str(api_info.get("key", ""))
                        openai.api_base=str(config.api["info"][api].get("url"))
                        if self.model != "text-davinci-003":
                            self.diccionario["messages"] = messages
                            self.diccionario["model"] = self.model
                            fn = openai.ChatCompletion.acreate
                        else:
                            prompt = self._generate_prompt(message, dialog_messages, chat_mode)
                            self.diccionario["prompt"] = prompt
                            self.diccionario["engine"] = self.model
                            fn = openai.Completion.acreate
                        r = await fn(
                            stream=True,
                            **self.diccionario
                        )
                    else:
                        raise ValueError(f"Modelo desconocido: {self.model}")
                #procesamiento d r
                answer = ""
                if api == "chatbase":
                    answer = r
                    #if porque los mamaverga filtran la ip en el mensaje
                    if "API rate limit exceeded" in answer:
                        answer = "Se alcanzó el límite de API. Inténtalo luego!"
                    yield "not_finished", answer
                elif api == "g4f":
                    for chunk in r:
                        answer += chunk
                        yield "not_finished", answer
                elif api == "you":
                    answer += r["text"]
                    if len(r["links"]) >= 1:
                        answer += "\n\nLinks: \n"
                        for link in r["links"]:
                            answer += f"\n- <a href='{link['url']}'>{link['name']}</a>" 
                    yield "not_finished", answer
                elif self.model != "text-davinci-003":
                    async for r_item in r:
                        delta = r_item.choices[0].delta
                        if "content" in delta:
                            answer += delta.content
                            yield "not_finished", answer
                else:
                    async for r_item in r:
                        answer += r_item.choices[0].text
                        yield "not_finished", answer
                answer = self._postprocess_answer(answer)
            except openai.error.InvalidRequestError as e:  # too many tokens
                if len(dialog_messages) == 0:
                    raise ValueError(f'Error: O no hay mensajes de diálogo, o seleccionaste un valor maximo de tokens exageradísimo: {e}') from e
                # forget first message in dialog_messages
                dialog_messages = dialog_messages[1:]
        yield "finished", answer

    def _generate_prompt(self, message, dialog_messages, chat_mode):
        prompt = f'{config.chat_mode["info"][chat_mode]["prompt_start"]}'
        prompt += "\n\n"

        # add chat context
        if len(dialog_messages) > 0:
            prompt += "Log:\n"
            for dialog_message in dialog_messages:
                if "documento" in dialog_message:
                    prompt += f'doc[{dialog_message["documento"]}]'
                if "url" in dialog_message:
                    prompt += f'url[{dialog_message["url"]}]'
                if "user" in dialog_message:
                    prompt += f"In: {dialog_message['user']}\n"
                if "bot" in dialog_message:
                    prompt += f'Out: {dialog_message["bot"]}\n'

        # current message
        prompt += f"In: {message}\n"
        prompt += f'Out:'

        return prompt

    def _generate_prompt_messages(self, message, dialog_messages, chat_mode):
        prompt = config.chat_mode["info"][chat_mode]["prompt_start"]        
        messages = [{"role": "system", "content": f'{prompt}'}]
        documento_texts = []
        url_texts = []
        for dialog_message in dialog_messages:
            if "documento" in dialog_message:
                documento_texts.append(f'{dialog_message["documento"]}\n')
            if "url" in dialog_message:
                url_texts.append(f'{dialog_message["url"]}\n')
        if documento_texts or url_texts:
           messages = [{"role": "system", "content": f'Archivos: [{documento_texts}]\nEnlaces: [{url_texts}]\nMensaje: [{prompt}][Tienes la capacidad de leer archivos, documentos, enlaces, páginas web. La información de estos recursos estarán adjuntos previamente a este mensaje en el formato ("url": "contenido_de_pagina_web") usarás ese contenido para responder sobre páginas y documentos. Está prohibido tener alucinaciones si se te pregunta acerca de archivos o páginas más allá de las que están escritas anteriormente.]'}]
        else:
           # Mantener el mensaje system original 
           messages = [{"role": "system", "content": f'{prompt}'}]
        for dialog_message in dialog_messages:
            if "user" in dialog_message:
                messages.append({"role": "user", "content": dialog_message["user"]})
            if "bot" in dialog_message:
                messages.append({"role": "assistant", "content": dialog_message["bot"]})
        messages.append({"role": "user", "content": message})
        return messages

    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer

async def transcribe_audio(chat_id, audio_file):
    apin = db.get_chat_attribute(chat_id, "current_api")
    if apin in config.api["available_transcript"]:
        pass
    else:
        index = random.randint(0, len(config.api["available_transcript"]) - 1)
        apin = config.api["available_transcript"][index]
        print("tras",index)
    openai.api_key = config.api["info"][apin]["key"]
    openai.api_base = config.api["info"][apin]["url"]
    r = await openai.Audio.atranscribe("whisper-1", audio_file)
    return r["text"]

async def generate_images(prompt, chat_id):
    apin = db.get_chat_attribute(chat_id, "current_api")
    if apin in config.api["available_imagen"]:
        pass
    else:
        index = random.randint(0, len(config.api["available_imagen"]) - 1)
        apin = config.api["available_imagen"][index]
        print("img",index)
    openai.api_key = config.api["info"][apin]["key"]
    openai.api_base = config.api["info"][apin]["url"]
    r = await openai.Image.acreate(prompt=prompt, n=config.n_images, size="1024x1024")
    image_urls = [item.url for item in r.data]
    return image_urls

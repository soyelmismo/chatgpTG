import config
import openai
import database
from apis.gpt4free import g4f
from apis.opengpt import chatbase
from apis.gpt4free.foraneo import you


db = database.Database()
   
class ChatGPT:
    def __init__(self, model="gpt-3.5-turbo"):
        assert model in config.model["available_model"], f"Unknown model: {model}"
        self.model = model

    async def send_message(self, message, user_id, dialog_messages=[], chat_mode="assistant"):
        api = db.get_user_attribute(user_id, "current_api")
        current_max_tokens = db.get_user_attribute(user_id, "current_max_tokens")
        api_info = config.api["info"].get(api, {})
        openai.api_key = str(api_info.get("key", ""))
        openai.api_base=str(config.api["info"][api].get("url"))
        answer = None
        while answer is None:
            try:
                messages = self._generate_prompt_messages(message, dialog_messages, chat_mode)
                if api == "chatbase":
                    r = chatbase.GetAnswer(messages=messages, model=self.model)
                elif api == "g4f":
                    provider_name = config.model['info'][self.model]['name']
                    provider = getattr(g4f.Providers, provider_name)
                    # streamed completion
                    r = g4f.ChatCompletion.create(provider=provider, model='gpt-3.5-turbo', messages=messages, stream=True)
                elif api == "you":
                    r = you.Completion.create(
                        prompt=messages,
                        chat=dialog_messages,
                        detailed=False,
                        include_links=True, )
                    r = dict(r)
                else:
                    config.completion_options["max_tokens"] = int(config.max_tokens["info"][current_max_tokens]["name"])
                    if (self.model in config.model["available_model"]):
                        if self.model != "text-davinci-003":
                            config.completion_options["messages"] = messages
                            config.completion_options["model"] = self.model
                            fn = openai.ChatCompletion.create
                        else:
                            prompt = self._generate_prompt(message, dialog_messages, chat_mode)
                            config.completion_options["prompt"] = prompt
                            config.completion_options["engine"] = self.model
                            fn = openai.Completion.create
                        r = await fn(
                            stream=True,
                            **config.completion_options
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
                    raise ValueError("Mensajes de diálogo se reduce a cero, pero todavía tiene demasiados tokens para hacer la finalización") from e
                # forget first message in dialog_messages
                dialog_messages = dialog_messages[1:]
        yield "finished", answer

    def _generate_prompt(self, message, dialog_messages, chat_mode):
        prompt = f'system_message({config.chat_mode["info"][chat_mode]["prompt_start"]})'
        prompt += "\n\n"

        # add chat context
        if len(dialog_messages) > 0:
            #prompt += "Chat:\n"
            for dialog_message in dialog_messages:
                prompt += f"User: {dialog_message['user']}\n"
                prompt += f'{chat_mode}: {dialog_message["bot"]}\n'

        # current message
        prompt += f"User: {message}\n"
        prompt += f'{chat_mode}'

        return prompt

    def _generate_prompt_messages(self, message, dialog_messages, chat_mode):
        prompt = config.chat_mode["info"][chat_mode]["prompt_start"]
        messages = [{"role": "system", "content": f'{chat_mode} {prompt}'}]
        for dialog_message in dialog_messages:
            messages.append({"role": "user", "content": dialog_message["user"]})
            messages.append({"role": "assistant", "content": dialog_message["bot"]})
        messages.append({"role": "user", "content": message})

        return messages
    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer

async def transcribe_audio(user_id, audio_file):
    api = db.get_user_attribute(user_id, "current_api")
    api_info = config.api["info"].get(api, {})
    openai.api_key = str(api_info.get("key", ""))
    openai.api_base=str(config.api["info"][api].get("url"))
    r = await openai.Audio.atranscribe("whisper-1", audio_file)
    return r["text"]

async def generate_images(prompt, user_id):
    api = db.get_user_attribute(user_id, "current_api")
    api_info = config.api["info"].get(api, {})
    openai.api_key = str(api_info.get("key", ""))
    openai.api_base=str(config.api["info"][api].get("url"))
    r = await openai.Image.acreate(prompt=prompt, n=config.n_images, size="1024x1024")
    image_urls = [item.url for item in r.data]
    return image_urls

async def is_content_acceptable(prompt):
    r = await openai.Moderation.acreate(input=prompt)
    return not all(r.results[0].categories.values())

from bot.src.utils import config

async def _make_api_call(self, **kwargs):
    try:
        api_functions = {
            "chatbase": _chatbase,
            "g4f": _g4f,
            "you": _you,
            "evagpt4": _evagpt4
        }
        self.answer = ""

        api_function = api_functions.get(self.api, _openai)
        async for status, self.answer in api_function(self, **kwargs):
            yield status, self.answer
    except Exception as e:
        e = f'_make_api_call: {e}'
        raise Exception(e)

async def _openai(self, **kwargs):
    import openai
    try:
        api_info = config.api["info"].get(self.api, {})
        openai.api_key = str(api_info.get("key", ""))
        openai.api_base=str(config.api["info"][self.api].get("url"))
        self.diccionario.update({"messages": kwargs["messages"], "model": self.model} if kwargs["messages"] != None else {"prompt": kwargs["prompt"], "engine": self.model})
        fn = openai.ChatCompletion.acreate if kwargs["messages"] != None else openai.Completion.acreate

        r = await fn(stream=True, **self.diccionario)
        async for r_item in r:
            if kwargs['messages'] != None:
                delta = r_item.choices[0].delta
                if "content" in delta:
                    self.answer += delta.get("content", "")
            else:
                self.answer += r_item.choices[0].text
            yield "not_finished", self.answer
    except Exception as e:
        e = f'_get_openai_answer: {e}'
        raise Exception(e)

async def _you(self, **kwargs):
    try:
        from apis.gpt4free.foraneo import you
        r = you.Completion.create(
            prompt=kwargs['messages'],
            chat=kwargs['dialog_messages'],
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
        
async def _chatbase(self, **kwargs):
    try:
        from apis.opengpt import chatbase
        r = chatbase.GetAnswer(messages=kwargs['messages'], model=self.model)
        for chunk in r:
            self.answer += chunk
            if "API rate limit exceeded" in self.answer:
                raise RuntimeError(config.lang["errores"]["utils_chatbase_limit"][self.lang])
            yield "not_finished", self.answer
    except Exception as e:
        e = f'_get_chatbase_answer: {e}'
        raise Exception(e)
async def _evagpt4(self, **kwargs):
    try:
        from apis.opengpt import evagpt4
        r = evagpt4.Model(model=self.model).ChatCompletion(messages=kwargs['messages'])
        for chunk in r:
            self.answer += chunk
            yield "not_finished", self.answer
    except Exception as e:
        e = f'_get_evagpt4_answer: {e}'
        raise Exception(e)
    
async def _g4f(self, **kwargs):
    try:
        from apis.gpt4free import g4f
        provider_name = config.model['info'][self.model]['name']
        provider = getattr(g4f.Providers, provider_name)
        r = g4f.ChatCompletion.create(provider=provider, model='gpt-3.5-turbo', messages=kwargs['messages'], stream=True)
        for chunk in r:
            self.answer += chunk
            yield "not_finished", self.answer
    except Exception as e:
        e = f'_get_g4f_answer: {e}'
        raise Exception(e)
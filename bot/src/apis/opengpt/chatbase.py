import aiohttp

async def create(self):
    if self.model == "gpt-4":
        chat_id = "quran---tafseer-saadi-pdf-wbgknt7zn"
    elif self.model == "gpt-3.5-turbo":
        chat_id = "chatbase--1--pdf-p680fxvnm"

    data = {
        "messages": self.diccionario["messages"],
        "captchaCode": "hadsa",
        "chatId": chat_id,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://www.chatbase.co/api/fe/chat", json=data, proxy=self.proxies) as response:
            try:
                async for line in response.content:
                    line_text = line.decode("utf-8").strip()
                    if "API rate limit exceeded" in line_text:
                        line_text = f'{self.config.lang[self.lang]["errores"]["utils_chatbase_limit"]}'
                        yield "finished", line_text
                        break
                    yield "not_finished", line_text
            except Exception as e:
                print(f'{__name__}: {e}')

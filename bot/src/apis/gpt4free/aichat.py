from aiohttp import ClientSession
from ujson import loads
headers = {
    'authority': 'chat-gpt.org',
    'accept': '*/*',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://chat-gpt.org',
    'pragma': 'no-cache',
    'referer': 'https://chat-gpt.org/chat',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
}

async def create(self):

    async with ClientSession() as session:
        async with session.post('https://chat-gpt.org/api/text',
                                headers=headers,
                                json=self.diccionario, proxy=self.proxies) as response:
            try:
                response.raise_for_status()
                async for line in response.content:
                    line_text = line.decode("utf-8").strip()
                    data_json = loads(line_text)
                    if "quota" in data_json.get("error"):
                        line_text = f'{self.config.lang[self.lang]["errores"]["utils_chatbase_limit"]}'
                        yield "finished", line_text
                        break
                    yield "not_finished", data_json["message"]
            except Exception as e:
                raise ConnectionError(f"{__name__}: {e}")

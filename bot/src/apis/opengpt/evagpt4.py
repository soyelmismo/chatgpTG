import aiohttp
import json

async def create(self):

    async with aiohttp.ClientSession() as session:
        async with session.post("https://ava-alpha-api.codelink.io/api/chat",
                                headers={"content-type": "application/json"},
                                data=json.dumps(self.diccionario), proxy=self.proxies) as response:
            try:
                async for line in response.content:
                    try:
                        line_text = line.decode("utf-8").strip()

                        data_json = json.loads(line_text[len("data:"):])

                        choices = data_json.get("choices", [])

                        if not choices:
                            continue

                        for choice in choices:
                            if choice.get("finish_reason") == "stop":
                                break

                            if "delta" in choice and "content" in choice.get("delta"):
                                content = choice.get("delta", {}).get("content", "")
                                yield "not_finished", content
                    except (json.JSONDecodeError, IndexError, KeyError):
                        continue
            except Exception as e:
                raise ConnectionError(f'{__name__}: {e}')

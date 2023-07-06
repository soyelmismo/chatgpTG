import aiohttp
import json

async def create(self):
    async with aiohttp.ClientSession() as session:
        async with session.post("https://us-central1-arched-keyword-306918.cloudfunctions.net/run-inference-1", json={"prompt": self.diccionario["prompt"]}, proxy=self.proxies) as response:
            try:
                async for line in response.content:
                    yield "not_finished", json.loads(line).get("completion")
            except Exception as e:
                raise ConnectionError(f"{__name__}: {e}")
                return
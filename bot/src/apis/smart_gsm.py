from aiohttp import ClientSession
from ujson import loads
from bot.src.handlers.url import extract_from_url

base = "https://www.smart-gsm.com/moviles"
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36" 
}

async def get_device(self, query: str = ""):

    url = f"{base}/autocomplete/{query}"

    async with ClientSession() as session:
        try:
            async with session.get(url, headers=headers, proxy=self.proxies) as resp:
                data = await resp.text()
                response_obj = loads(data)
                if not response_obj: return "Dile al usuario que falló la búsqueda o que posiblemente no exista ese modelo de telefono"

                permalink = response_obj[0].get("permalink")
                if not permalink: return "Dile al usuario que falló la búsqueda o que posiblemente no exista ese modelo de telefono"

                data = await extract_from_url(f"{base}/{permalink}")
                return data
        except Exception as e: raise ConnectionError(e)

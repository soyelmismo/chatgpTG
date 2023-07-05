import httpx
import asyncio
from json import loads
from bot.src.handlers.url import extract_from_url

async def get_device(self, query: str = ""):

    base = "https://www.smart-gsm.com/moviles"
    url = f"{base}/autocomplete/{query}"
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36" 
    }

    async with httpx.AsyncClient(proxies=self.proxies) as client:
        try:
            data = await client.get(url, headers=headers)
            response_obj = loads(data.text)
            if not response_obj: return "Dile al usuario que falló la búsqueda o que posiblemente no exista ese modelo de telefono"

            permalink = response_obj[0].get("permalink")
            if not permalink: return "Dile al usuario que falló la búsqueda o que posiblemente no exista ese modelo de telefono"

            data = await extract_from_url(f"{base}/{permalink}")
            return data
        except Exception as e: raise ConnectionError(e)

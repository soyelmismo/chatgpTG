import httpx

async def get_ip():
    url = "http://mip.resisto.rodeo"  # Reemplaza con tu dominio o dirección IP

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        ip = response.text.strip()  # Elimina espacios en blanco alrededor de la IP
        return ip

async def resetip(self):
    global ip
    new_ip = await get_ip()

    if not ip or ip != new_ip:
        if await process_request(self):
            ip = new_ip
            return True

    return None

async def process_request(self):
    if self.api == "cattto":
        url = "http://api.cattto.repl.co/resetip"
    elif self.api == "chatpawan":
        url = "http://api.pawan.krd/resetip"
    else:
        return None

    from bot.src.utils.config import api
    api_info = api["info"].get(self.api, {})
    key = str(api_info.get("key", ""))
    headers = {"Authorization": "Bearer " + key}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        return response is not None

ip = None
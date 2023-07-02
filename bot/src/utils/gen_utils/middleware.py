import httpx

async def get_ip(self):
    url = "http://mip.resisto.rodeo"  # Reemplaza con tu dominio o dirección IP

    async with httpx.AsyncClient(proxies=self.proxies) as client:
        response = await client.get(url)
        ip = response.text.strip()  # Elimina espacios en blanco alrededor de la IP
        print(ip)
        return ip

async def resetip(self):
    global apisdict
    new_ip = await get_ip(self)
    if not apisdict.get(self.api):
        apisdict[self.api] = {"ip": None}
    if not apisdict.get(self.api).get("ip") or apisdict.get(self.api).get("ip") != new_ip:
        if await process_request(self):
            apisdict[self.api]["ip"] = new_ip
            print(apisdict)
            return True

    return None

async def process_request(self):
    from bot.src.utils.config import api
    if api["info"][self.api].get("resetip"):
        url = str(api["info"][self.api].get("resetip"))
    else:
        return None

    async with httpx.AsyncClient(proxies=self.proxies) as client:
        response = await client.post(url, headers={"Authorization": "Bearer " + str(api["info"].get(self.api, {}).get("key", ""))})
        print(response)
        return response is not None

apisdict = {}
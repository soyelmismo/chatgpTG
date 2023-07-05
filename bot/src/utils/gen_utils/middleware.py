import aiohttp

async def get_ip(proxy=None):
    url = "https://mip.resisto.rodeo"  # Reemplaza con tu dominio o dirección IP
    headers = {
        "Accept": "*/*",
        "User-Agent": "GPTG" 
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, proxy=proxy) as response:
            ip = await response.text()
            ip = ip.strip()  # Elimina espacios en blanco alrededor de la IP
            return ip

async def resetip(self):
    from bot.src.utils.config import api
    if not api["info"][self.api].get("resetip"):
        return None

    global apisdict
    if self.proxies:
        proxy = next(iter(self.proxies.values()))
    else:
        proxy = None
    new_ip = await get_ip(proxy)
    print(new_ip)
    if not apisdict.get(self.api):
        apisdict[self.api] = {"ip": None}
    if not apisdict.get(self.api).get("ip") or apisdict.get(self.api).get("ip") != new_ip:
        if await process_request(self, api, proxy):
            apisdict[self.api]["ip"] = new_ip
            print(apisdict)
            return True

    return None

async def process_request(self, api, proxy=None):
    url = str(api["info"][self.api].get("resetip"))

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers={"Authorization": "Bearer " + str(api["info"].get(self.api, {}).get("key", ""))}, proxy=proxy) as response:
                call = await response.text()
        except Exception as e:
            print(f'Error {__name__}: {e}')
            return None
        return call

apisdict = {}
from datetime import datetime

async def task():
    from bot.src.utils.proxies import cache_index, lang_cache, chat_mode_cache, api_cache, model_cache, menu_cache, interaction_cache, sleep, asyncio
    while True:
        try:
            for cache in cache_index:
                if cache is not None:
                    if isinstance(cache, dict):
                        for key, value in list(cache.items()):
                            if datetime.now() > value[1]: del cache[key]
        except asyncio.CancelledError:
            break
        await sleep(60 * 60)


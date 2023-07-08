async def gen(self, prompt, current_api, style, ratio, model, seed=None, negative=None):
    try:
        from bot.src.utils.proxies import config
        #from bot.src.apis import imagine
        #if current_api == "imaginepy":
        #    image, seed = await imagine.main(self, prompt=prompt, style=style, ratio=ratio, model=model, seed=seed, negative=negative, endpoint=config.custom_imaginepy_url)
        #    return image, seed
        #else:
        import openai
        if self.proxies is not None:
            openai.proxy = {f'{config.proxy_raw.split("://")[0]}': f'{config.proxy_raw}'}
        openai.api_key = config.api["info"][current_api]["key"]
        openai.api_base = config.api["info"][current_api]["url"]
        r = await openai.Image.acreate(prompt=prompt, n=config.n_images, size="1024x1024")
        image_urls = [item.url for item in r.data]
        return image_urls, None
    except Exception as e:
        raise RuntimeError(f'make_image.gen > {e}')
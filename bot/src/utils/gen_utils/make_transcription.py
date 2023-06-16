async def write(self, audio_file):
    from bot.src.utils import config
    import random
    import openai
    if self.api not in config.api["available_transcript"]:
        index = random.randint(0, len(config.api["available_transcript"]) - 1)
        self.api = config.api["available_transcript"][index]
    openai.api_key = config.api["info"][self.api]["key"]
    openai.api_base = config.api["info"][self.api]["url"]
    r = await openai.Audio.atranscribe("whisper-1", audio_file)
    return r["text"]
import aiohttp
import asyncio
import io
import uuid
import secrets
import base64

api_base = 'https://stablehorde.net/api/v2'
check_url = f'{api_base}/generate/check'
status_url = f'{api_base}/generate/status'


from bot.src.utils.config import apisproxy, n_images
from bot.src.utils.constants import logger

stablehorde_models = None

class Models:
    def __init__(self, model_name):
        self.model_name = model_name

    @classmethod
    async def get_models(cls, proxy=None):
        url = f'{api_base}/status/models'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy) as response:
                data = await response.json()

        sorted_data = sorted(data, key=lambda x: x["count"], reverse=True)
        
        for model in sorted_data:
            model["name"] = f'{model["name"]} ({model["count"]})'

        image_models = [model["name"] for model in sorted_data if model["type"] == "image" and int(model["count"]) > 5]
        models = {index: cls(model_name) for index, model_name in enumerate(image_models)}

        return models
        
async def setup_vars():
    global stablehorde_models
    models_sh = await Models.get_models(proxy=apisproxy)
    stablehorde_models = {index: model_instance.model_name for index, model_instance in models_sh.items()}
    # Resto del código que utiliza stablehorde_models
loop = asyncio.get_event_loop()
loop.run_until_complete(setup_vars())


async def main(self, api_key, prompt: str = 'egg', model: str = 'Deliberate',
               seed = None, steps: int = 20, n_images: int = n_images):

    model = stablehorde_models.get(int(model))
    model = model.split('(', 1)[0].strip()

    url = f'{api_base}/generate/async'

    headers = {
        "apikey": f'{api_key}',
        "Content-Type": "application/json",
        "Accept": "*/*"
    }

    payload = {
        "prompt": prompt,
        "params": {
            "steps": steps,
            "n": 1,
            "sampler_name": "k_euler",
            "width": 512,
            "height": 512,
            "cfg_scale": 7,
            "seed_variation": 1000,
            "seed": str(seed) if seed else "",
            "karras": True,
            "denoising_strength": 0.75,
            "tiling": False,
            "hires_fix": True,
            "clip_skip": 1,
            #"post_processing": [
            #    "GFPGAN",
            #    "RealESRGAN_x4plus_anime_6B"
            #]
        },
        "nsfw": True,
        "censor_nsfw": False,
        "trusted_workers": False,
        "models": [
            model
        ],
        #"workers": [
        #],
        "shared": False,
        #"slow_workers": False,
        "r2": False,
        "jobId": "",
        "index": 0,
        "gathered": False,
        "failed": False
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Etapa 1: Recibir ID
            job_id = None
            try:
                while not job_id:
                    async with session.post(url, headers=headers, json=payload, proxy=self.proxies) as response:
                        data = await response.json()
    
                        job_id = data.get('id', None)
                        await asyncio.sleep(1)
            except Exception as e: logger.error(f'etapa1 > {e}')
            if not job_id: raise ValueError("No job ID")
            # Esperar hasta que el valor de "done" sea True
            done = False
            try:
                while not done:
                    async with session.get(f'{check_url}/{job_id}', proxy=self.proxies) as response:
                        data = await response.json()
                        #estado = f'⏳ {data["wait_time"]}s\n ID: {job_id}'
                        done = data['done']
                        await asyncio.sleep(2)  # Esperar 1 segundo antes de volver a verificar
            except Exception as e: logger.error(f'etapa2 > {e}')
            # Obtener la URL de la imagen generada
            try:
                async with session.get(f'{status_url}/{job_id}', proxy=self.proxies) as response:
                    data = await response.json()
                    
                    generations = data['generations']
            except Exception as e: 
                logger.error(f'etapa3> {e}')
            
            img_dict = {}

            for generation in generations:
                img = generation['img']
                seed = generation['seed']
                id = generation['id']
                try:
                    img_data = base64.b64decode(img)
                    img_io = io.BytesIO(img_data)
                    img_io.name = f"{seed} - {id}.png"
                    img_dict[seed] = img_io
                except Exception as e: 
                    logger.error(f'Error fetching image: {e}')
            img_io_list = list(img_dict.values())
            #asyncio.create_task(setup_vars())
            return img_io_list, seed, model
            
    except Exception as e: logger.error(f'stablehorde.main > {e}')
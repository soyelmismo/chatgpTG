#from .imaginepy import AsyncImagine, Style, Ratio, Model
import uuid
import io
import secrets
AsyncImagine, Style, Ratio, Model = None, None, None, None
async def main(self, prompt, style, ratio, model, seed=None, negative=None, endpoint=None):
    imagine = AsyncImagine(api=endpoint, proxies=self.proxies)
    try:
        if seed == None:
            seed = secrets.randbelow(10**16)

        img_data = await imagine.sdprem(
            prompt=prompt,
            model=Model.__members__[model],
            style=Style.__members__[style],
            ratio=Ratio.__members__[ratio],
            negative=negative,
            seed=seed,
            cfg=15,
            high_result = 1,
            priority = 1,
            steps = 50
        )
        await imagine.close()
    except Exception as e:
        raise BufferError(f"error imagine.py: {e}")

    try:    
        imagine = AsyncImagine()
        img_data = await imagine.upscale(image=img_data)

        await imagine.close()

        if img_data == None:
            raise FileNotFoundError("no files")

    except Exception as e:
        raise BufferError(f"error imagine.py: {e}")

    img_io = io.BytesIO(img_data)
    img_io.name = f"{uuid.uuid4()}.png"
    return img_io, seed
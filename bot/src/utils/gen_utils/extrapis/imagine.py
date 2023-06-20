from imaginepy import AsyncImagine, Style, Ratio
import uuid
import io
import secrets

async def main(prompt, style, ratio, seed=None):
    imagine = AsyncImagine()
    try:
        if seed == None:
            seed = secrets.randbelow(10**16)
        img_data = await imagine.sdprem(
            prompt = prompt,
            style = Style.__members__[style],
            ratio = Ratio.__members__[ratio],
            seed =  seed,
            steps = 300
        )
        img_data = await imagine.upscale(image=img_data)
    except Exception as e:
        raise BufferError(f"An error occurred while generating the image: {e}")
    finally:
        await imagine.close()
    img_io = io.BytesIO(img_data)
    img_io.name = f"{uuid.uuid4()}.png"
    return img_io, seed
from bot.src.start import Update, CallbackContext
from datetime import datetime
from pathlib import Path
import tempfile
from . import semaphore as tasks
from ..utils.misc import clean_text, add_dialog_message
async def handle(chat, lang, update, context):
    from bot.src.utils.proxies import (
    ChatAction, ParseMode, config,
    interaction_cache, db
    )
    image = update.message.photo[-1]
    from PIL import Image
    import pytesseract
    #import cv2
    import numpy as np
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            await update.effective_chat.send_action(ChatAction.TYPING)
            tmp_dir = Path(tmp_dir)
            img_path = tmp_dir / Path("ocrimagen.jpg")
            image_file = await context.bot.get_file(image.file_id)
            await image_file.download_to_drive(img_path)
            imagen = Image.open(str(img_path))
            #imagen = cv2.imread(str(img_path))
            #gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            #_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            #coords = np.column_stack(np.where(binary > 0))
            #rect = cv2.minAreaRect(coords)
            #angle = rect[-1]
            #if angle < -45:
            #    angle = -(90 + angle)
            #else:
            #    angle = -angle
            #(h, w) = imagen.shape[:2]
            #center = (w // 2, h // 2)
            #matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            #rotated = cv2.warpAffine(imagen, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            doc = pytesseract.image_to_string(imagen, timeout=50, lang='spa+ara+eng+jpn+chi+deu+fra+rus+por+ita+nld', config='--psm 3')
            interaction_cache[chat.id] = ("visto", datetime.now())
            await db.set_chat_attribute(chat, "last_interaction", datetime.now())
            if len(doc) <= 1:
                text = f'{config.lang["errores"]["error"][lang]}: {config.lang["errores"]["ocr_no_extract"][lang]}'
            else:
                doc = await clean_text(doc)
                text = config.lang["mensajes"]["image_ocr_ask"][lang].format(ocresult=doc)
                new_dialog_message = {"user": f'{config.lang["metagen"]["transcripcion_imagen"][lang]}: "{doc}"', "date": datetime.now()}
                await add_dialog_message(chat, new_dialog_message)
    except RuntimeError:
        text = f'{config.lang["errores"]["error"][lang]}: {config.lang["errores"]["tiempoagotado"][lang]}'
    await update.message.reply_text(f'{text}', parse_mode=ParseMode.MARKDOWN)
    await tasks.releasemaphore(chat=chat)
async def wrapper(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (bb,obtener_contextos as oc, debe_continuar)
    if not update.effective_message.photo: return
    chat, lang = await oc(update)
    if not await debe_continuar(chat, lang, update, context): return
    task = bb(handle(chat, lang, update, context))
    await tasks.handle(chat, lang, task, update)

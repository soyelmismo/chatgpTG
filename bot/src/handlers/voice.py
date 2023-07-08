from subprocess import call
from udatetime import now
from bot.src.start import Update, CallbackContext
from tempfile import TemporaryDirectory
from pathlib import Path
from bot.src.utils.gen_utils.phase import ChatGPT
async def handle(chat, lang, update, context):
    from . import semaphore as tasks
    from bot.src.utils.proxies import (logger,db,interaction_cache,config,ChatAction,errorpredlang)
    # Procesar sea voz o audio
    if update.message.voice: audio = update.message.voice
    elif update.message.audio: audio = update.message.audio
    else: return
    file_size_mb = audio.file_size / (1024 * 1024)
    transcribed_text = None
    if file_size_mb <= config.audio_max_size:
        try:
            await update.effective_chat.send_action(ChatAction.TYPING)
            with TemporaryDirectory() as tmp_dir:
                # Descargar y convertir a MP3
                tmp_dir = Path(tmp_dir)
                ext = audio.mime_type
                from mimetypes import guess_extension
                if ext == 'audio/opus': ext = '.opus'
                else: ext = guess_extension(ext)
                doc_path = tmp_dir / Path("tempaudio" + ext)

                # download
                voice_file = await context.bot.get_file(audio.file_id)
                await voice_file.download_to_drive(doc_path)

                # convert to mp3
                mp3_file_path = tmp_dir / "voice.mp3"
                call(f"sox {doc_path} -C 64 -r 16000 -q {mp3_file_path} > /dev/null 2>&1", shell=True)

                # Transcribir
                with open(mp3_file_path, "rb") as f:
                    await tasks.releasemaphore(chat=chat)
                    insta = await ChatGPT.create(chat)
                    transcribed_text = await insta.transcribe(f)

            # Enviar respuesta            
            text = f"🎤 {transcribed_text}"
            interaction_cache[chat.id] = ("visto", now())
            await db.set_chat_attribute(chat, "last_interaction", now())
        except Exception as e:
            logger.error(f'{__name__}: <transcribe_message_handle> {errorpredlang}: {e}')
            await tasks.releasemaphore(chat=chat)
    else:
        text = f'{config.lang[lang]["errores"]["audio_size_limit"].format(audio_max_size=config.audio_max_size)}'
    from bot.src.utils.misc import send_large_message
    await send_large_message(text, update)
    await tasks.releasemaphore(chat=chat)
    if transcribed_text:
        from . import message
        await message.handle(chat, lang, update, context, _message=transcribed_text)
async def wrapper(update: Update, context: CallbackContext):
    from bot.src.utils.proxies import (debe_continuar,obtener_contextos as oc, bb)
    chat, lang = await oc(update)
    if not await debe_continuar(chat, lang, update, context, bypassmention=True): return
    task = bb(handle(chat, lang, update, context))
    from . import semaphore as tasks
    await tasks.handle(chat, task)

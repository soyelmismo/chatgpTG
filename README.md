## Comandos:
- /new - Iniciar nuevo diálogo.
- /img - Generar imagenes.
- /retry - Regenera la última respuesta del bot.
- /chat_mode - Seleccionar el modo de conversación.
- /model - Mostrar modelos IA.
- /api - Mostrar APIs.
- /lang - Ver idiomas disponibles.
- /help – Mostrar este mensaje de nuevo.

## Características:
- Envía un archivo de texto, PDF o URL y el bot los podrá analizar!
- Añade proxies reversos de OpenAI y sus respectivos modelos cuanto quieras!
- Multi lenguaje.
- Lee el texto de imágenes
- Transcribe audios

# Historial de estrellas

[![Star History Chart](https://api.star-history.com/svg?repos=soyelmismo/chatgpTG&type=Date)](https://star-history.com/#soyelmismo/chatgpTG&Date)


## Nueva actualización:
- Código de verificador de APIs re hecho.
- Código del menu re hecho y añadido paginación.
- Código de peticiones a APIs re hecho.
- Mejor gestión de errores.
- Se añadieron variables a docker-compose para habilitar o deshabilitar características del bot a elección del administrador.
- Se corrigió el streaming de algunas APIs

## Cambios anteriores:
- *MultiLenguaje!*:
    - "es": Español
    - "ar": عربي
    - "en": English
    - "jp": 日本語
    - "zh": 中文
    - "de": Deutsch
    - "fr": Français
    - "ru": Русский
    - "pt": Português
    - "it": Italiano
    - "nl": Nederlands

Establece el idioma por defecto del sistema en la variable AUTO_LANG
Los lenguajes están *COMPLETAMENTE* traducidos... O eso creo.
- *Lectura de imágenes con OCR*
    - Gracias a Tesseract! Se agregó todos los lenguajes disponibles para el bot.
    - Si deseas desactivar lenguajes antes de construir el contenedor, estarán en Dockerfile.
- Se cambió el diálogo de usuarios, por el diálogo de chatID para mejor contexto grupal.
- Se mejoró el chequeo de APIs.
- Añadido MongoDB compatible con CPUs antiguas.
- Soporte de lectura de archivos de texto, PDF y de enlaces.
- Se reemplazó el modo "👩‍🎨 Artista básico" con el comando /img.
- <a href="https://github.com/karfly/chatgpt_telegram_bot/pull/112/commits/d54809aeb89a1921f6cfdffc00a4d1ee4744c8d2" alt="Dialog_ask">Preguntar si iniciar nueva conversación si lleva tiempo sin chatear</a> (TIMEOUT_ASK y DIALOG_TIMEOUT en docker-compose.yml)
- <a href="https://github.com/karfly/chatgpt_telegram_bot/pull/188" alt="AutoDel">Borrar historiales antiguos al usar /new.</a>
- Añadidas variables a docker-compose para limitar el tamaño de los audios, documentos, paginas de PDF y urls.
- La transcripción de mensajes de voz ahora también funciona para archivos de audio.
- Apis de GPT4Free (necesita especificar las cookies en docker-compose para usar Bing y ChatGPT)
- Base en Minideb.
- Se eliminó el seguimiento de tokens.
- Preferencias de API por usuario!
- Si la api actual del usuario no soporta voz o imagen, se usará una api predefinida.
- El generador de imágenes envía las imágenes comprimidas y en formato sin comprimir (archivo) 

# Importante:
- Las API personalizadas deben seguir la misma estructura de OpenAI, es decir, el "https://dominio.dom/v1/..."

## Setup
1. Obtén tu clave de [OpenAI API](https://openai.com/api/)

2. Obtén tu token de bot de Telegram de [@BotFather](https://t.me/BotFather)

3. Edita `config/api.example.yml` para configurar tu OpenAI-API-KEY o añadir apis personalizadas

4. Añade tu token de telegram, base de datos Mongo, modifica otras variables en 'docker-compose.example.yml' y renombra `docker-compose.example.yml` a `docker-compose.yml`

5. 🔥 Y ahora **ejecuta**:
    ```bash
    docker-compose up --build
    ```

## References
1. Origin: <a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>

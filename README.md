## Comandos:
- /new - Iniciar nuevo diálogo.
- /img - Generar imagenes.
- /retry - Regenera la última respuesta del bot.
- /chat_mode - Seleccionar el modo de conversación.
- /model - Mostrar modelos IA.
- /api - Mostrar APIs.
- /help – Mostrar este mensaje de nuevo.

## Características:
- Envía un archivo de texto, PDF o URL y el bot los podrá analizar!
- Añade proxies reversos de OpenAI y sus respectivos modelos cuanto quieras!


## Nueva actualización:
- Se mejoró el chequeo de APIs
- Añadido MongoDB compatible con CPUs antiguas.
- Soporte de lectura de archivos de texto, PDF y de enlaces.
- Se reemplazó el modo "👩‍🎨 Artista básico" con el comando /img.
- <a href="https://github.com/karfly/chatgpt_telegram_bot/pull/112/commits/d54809aeb89a1921f6cfdffc00a4d1ee4744c8d2" alt="Dialog_ask">Preguntar si iniciar nueva conversación si lleva tiempo sin chatear</a> (TIMEOUT_ASK y DIALOG_TIMEOUT en docker-compose.yml)
- <a href="https://github.com/karfly/chatgpt_telegram_bot/pull/188" alt="AutoDel">Borrar historiales antiguos al usar /new.</a>
- Añadidas variables a docker-compose para limitar el tamaño de los audios, documentos, paginas de PDF y urls.

## Cambios anteriores:
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
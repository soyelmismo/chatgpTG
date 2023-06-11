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
- Reestructuración de código.
- 2 comandos nuevos. /status y /reset
- Los comandos /help y /start ahora llaman a la API de GPT para ser asistente en la ayuda del bot.

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

- Bot: https://t.me/chismegptbpt
## Comandos:
- /new - Iniciar nuevo diálogo.
- /img - Generar imagenes.
- /retry - Regenera la última respuesta del bot.
- /chat_mode - Seleccionar el modo de conversación.
- /model - Mostrar modelos IA.
- /api - Mostrar APIs.
- /lang - Ver idiomas disponibles.
- /status - Ver la configuracion actual: Modelo, Modo de chat y API.
- /reset - Reestablece la configuración a valores predeterminados.
- /search - Busqueda en internet
- /help – Mostrar este mensaje de nuevo.

## Características:
- Haz que GPT acceda a Internet usando /search!
- Envía un archivo de texto, PDF o URL y el bot los podrá analizar!
- Añade proxies reversos de OpenAI y sus respectivos modelos cuanto quieras!
- Multi lenguaje.
- Lee el texto de imágenes
- Transcribe audios

# Historial de estrellas

<a href="https://gg.resisto.rodeo/yo/chatgpTG"><img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=soyelmismo/chatgpTG&type=Date"></a> 

## Nueva actualización:
- sistema de tiempo de espera y reintento.
- simplificación y mejora de las indicaciones.
- optimización de los mensajes cuando se alcanza el límite de tokens.
- utilizar el máximo de tokens posibles para completar / siempre por debajo del límite de tokens.
- Nuevas variables: REQUEST_MAX_RETRIES y REQUEST_TIMEOUT, REQUEST_TIMEOUT es en segundos.
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

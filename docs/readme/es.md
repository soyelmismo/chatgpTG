- Bot: https://t.me/chismegptbpt

[![es](https://img.shields.io/badge/Variables-es-yellow)](https://gg.resisto.rodeo/yo/chatgpTG/src/branch/main/docs/variables/es.md)

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
- Llamada a funciones! (plugins conectados directamente a GPT, modelos del mes de Junio>).
- Base de datos JSON local.
- Muy modular y personalizable.
- Haz que GPT acceda a Internet usando /search!
- Envía un archivo de texto, PDF o URL y el bot los podrá analizar!
- Añade proxies reversos de OpenAI y sus respectivos modelos cuanto quieras!
- Multi lenguaje.
- Lee el texto de imágenes.
- Transcribe audios.

# Importante:
- Las API personalizadas deben seguir la misma estructura de OpenAI, es decir, el "https://dominio.dom/v1/..."

## Setup
1. Obtén tu clave de [OpenAI API](https://openai.com/api/)

2. Obtén tu token de bot de Telegram de [@BotFather](https://t.me/BotFather)

3. Edita `config/api.example.json` para configurar tu API-KEY o añadir apis personalizadas

4. Añade tu token de telegram, base de datos Mongo, modifica otras variables en 'docker-compose.example.yml' y renombra `docker-compose.example.yml` a `docker-compose.yml`

5. 🔥 Accede al directorio desde la terminal y **ejecuta**:
    ```bash
    docker-compose up --build
    ```
# Historial de estrellas

<a href="https://gg.resisto.rodeo/yo/chatgpTG"><img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=soyelmismo/chatgpTG&type=Date"></a> 

## Referencias
1. Origen: <a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>

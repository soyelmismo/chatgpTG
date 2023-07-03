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
- Llamada a funciones! (plugins conectados directamente a GPT, modelos del mes de Junio>).
- Base de datos JSON local.
- Muy modular y personalizable.
- Haz que GPT acceda a Internet usando /search!
- Envía un archivo de texto, PDF o URL y el bot los podrá analizar!
- Añade proxies reversos de OpenAI y sus respectivos modelos cuanto quieras!
- Multi lenguaje.
- Lee el texto de imágenes.
- Transcribe audios.


## Nueva actualización:
- Migración de YAML a JSON. <a href="https://github.com/soyelmismo/YMLtoJSON">Ajusten sus archivos de configuracion.</a>
- Base de datos completamente local! Evitémonos de ejecutar un sistema gigantezco para administrar una base de datos de 1MB o menos :P (se activa con WITHOUT_MONGODB=True).
- Llamadas a funciones agregado! Pueden desactivarlo con la variable FEATURE_FUNCTION_CALLS=True/False
- Proxificacion de APIs exceptuando al bot, usen la variable API_TUNNEL=http://ip:puerto

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

## References
1. Origin: <a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>

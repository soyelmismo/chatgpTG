**Origin repo: <a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>**


## Características originales
- Mensaje en tiempo real
- Compatible con GPT-4
- Soporte de chat en grupo (/help_group_chat para obtener instrucciones)
- DALLE 2 (elige el modo 👩‍🎨 Artista para generar imágenes)
- Reconocimiento de mensajes de voz
- Resaltado de código en Markdown
- 15 modos de chat especiales: 👩🏼‍🎓 Asistente, 👩🏼‍💻 Asistente de código, 👩‍🎨 Artista, 🧠 Psicólogo, 🚀 Elon Musk y otros. Puedes crear fácilmente tus propios modos de chat editando `config/chat_mode.yml`.
- Soporte de [ChatGPT API](https://platform.openai.com/docs/guides/chat/introduction)
- Lista blanca de usuarios

## Nueva actualización:
- Voz a texto en archivos de audio
- Apis de GPT4Free


## Cambios base en esta modificación:
- Traducción al español
- Base en Minideb.
- Se eliminó el seguimiento de tokens, ya que no lo necesito.
- Se agregaron (creo que solo) 3 modos de chat. "Nada", "Matemático" y "Traductor" de cualquier idioma al español.
- Necesita base de datos mongo externa. Puedes montarla en un contenedor aparte o usar algún servicio como Atlas
- Sólo hay mensajes en tiempo real, no hay envío de mensaje fijo
- **Añade la cantidad de APIs y modelos que quieras!**
- Un menú genérico para los tipos de opciones
- "Simplificación" de ciertas partes del código
- Se añadió un comando /reboot para reiniciar el sistema Docker (está roto), los permisos del usuario se declaran en docker-compose.yml en la variable sudo_users
- Cambio de API por usuario!
- El generador de imágenes envía las imágenes comprimidas y en formato sin comprimir (archivo) 

# Importante:
- Las API personalizadas deben seguir la misma estructura de OpenAI, es decir, el "https://dominio.dom/v1/..."

## Comandos
- /retry - Regenera la última respuesta del bot.
- /new - Iniciar nuevo diálogo.
- /chat_mode - Seleccionar el modo de conversación.
- /model - Mostrar modelos IA.
- /api - Mostrar APIs.
- /help – Mostrar este mensaje de nuevo.

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
1. [*Build ChatGPT from GPT-3*](https://learnprompting.org/docs/applied_prompting/build_chatgpt)

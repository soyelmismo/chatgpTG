## Configuración

### Token de Telegram

Para usar el bot de Telegram, debes proporcionar un token de Telegram. Este token se puede obtener creando un bot a través de `https://t.me/botfather`. El token debe almacenarse en la variable `TELEGRAM_TOKEN`.

### Configuración del menú

El menú del bot se puede configurar con las siguientes opciones:

- `MAX_ITEMS_PER_PAGE`: El número máximo de elementos para mostrar por página en el menú. El valor predeterminado es 10.
- `MAX_COLUMNS_PER_PAGE`: El número máximo de columnas para mostrar por página en el menú. El valor predeterminado es 2.

### Lista blanca de usuarios y chats

Puedes especificar una lista blanca de usuarios y chats que tienen permitido interactuar con el bot. La lista blanca debe proporcionarse como una lista de IDs de usuario o chat en las variables `USER_WHITELIST` y `CHAT_WHITELIST`, respectivamente.

### Configuración de la base de datos

El bot admite tanto la base de datos MongoDB como la opción de base de datos JSON. De forma predeterminada, utiliza la base de datos Mongo. Para utilizar la base de datos JSON, establece la variable `WITHOUT_MONGODB` en `True`.

### Tiempo de espera del diálogo

El bot tiene una función de tiempo de espera del diálogo, que finaliza automáticamente una conversación si no hay actividad durante un cierto período de tiempo. La duración del tiempo de espera se puede configurar utilizando la variable `DIALOG_TIMEOUT`. El tiempo de espera predeterminado es de 7200 segundos (2 horas).

### Generación de imágenes

El bot admite la generación de imágenes basadas en la entrada del usuario. Para desactivar esta función, establece la variable `FEATURE_IMAGE_GENERATION` en `False`.

El número de imágenes a generar se puede configurar utilizando la variable `OUTPUT_IMAGES`. El valor predeterminado es 4 imágenes.

Las imágenes generadas tienen un tiempo de caducidad después del cual se eliminan de la memoria del bot. El tiempo de caducidad se puede configurar utilizando la variable `GENERATED_IMAGE_EXPIRATION_MINUTES`. El tiempo de caducidad predeterminado es de 5 minutos.

### Respuesta directa de URL

De forma predeterminada, el bot responde después de enviar una URL para que se lea. Para desactivar esto y esperar la entrada del usuario después de procesar la URL, establece la variable `URL_DIRECT_RESPONSE` en `False`.

### Respuestas en streaming

El bot responde con respuestas en streaming, lo que permite una salida continua de resultados. Para desactivar esta función, establece la variable `STREAM_ANSWERS` en `False`.

### Llamadas a funciones

El bot admite nuevas llamadas a funciones de OpenAI. Para desactivar esta función, establece la variable `FEATURE_FUNCTION_CALLS` en `False`.

### Pregunta de tiempo de espera

El bot tiene una función para preguntar si continuar o iniciar una nueva conversación. Si está desactivada, el bot eliminará automáticamente la conversación de tiempo de espera y comenzará una nueva. Para desactivar esta función, establece la variable `TIMEOUT_ASK` en `False`.

### Transcripción

El bot admite la transcripción de archivos de audio. Para desactivar esta función, establece la variable `FEATURE_TRANSCRIPTION` en `False`.

### OCR (Reconocimiento óptico de caracteres)

El bot admite OCR para leer texto de imágenes. Para desactivar esta función, establece la variable `FEATURE_IMAGE_READ` en `False`.

### Lectura de documentos

El bot admite la lectura de documentos. Para desactivar esta función, establece la variable `FEATURE_DOCUMENT_READ` en `False`.

### Búsqueda web

El bot admite la funcionalidad de búsqueda web. Para desactivar esta función, establece la variable `FEATURE_BROWSING` en `False`.

### Lectura de URL

El bot admite la lectura del contenido de las URL. Para desactivar esta función, establece la variable `FEATURE_URL_READ` en `False`.

### Límites de tamaño de audio y archivos

El bot tiene límites en el tamaño de los archivos de audio y documentos que se pueden procesar. El tamaño máximo de archivo de audio se puede configurar utilizando la variable `AUDIO_MAX_MB` (el valor predeterminado es de 20MB), y el tamaño máximo de archivo de documento se puede configurar utilizando la variable `DOC_MAX_MB` (el valor predeterminado es de 10MB).

### Límite de tamaño de URL

El bot tiene un límite en el tamaño de las URL que se pueden procesar. El tamaño máximo de URL se puede configurar utilizando la variable `URL_MAX_MB`. El límite predeterminado es de 5MB.

### Reintentos y tiempo de espera de las solicitudes

El bot admite reintentos de solicitud en caso de fallos. El número máximo de reintentos se puede configurar utilizando la variable `REQUEST_MAX_RETRIES`. El valor predeterminado es de 3 reintentos. La duración del tiempo de espera de la solicitud se puede configurar utilizando la variable `REQUEST_TIMEOUT`. El tiempo de espera predeterminado es de 10 segundos.

### Límite de páginas de PDF

Al leer documentos PDF, el bot tiene un límite en el número de páginas que se pueden procesar. El límite máximo de páginas se puede configurar utilizando la variable `PDF_PAGE_LIMIT`. El límite predeterminado es de 25 páginas.

### Detección automática de idioma

El bot admite la detección automática de idioma para el contexto y los menús. El idioma predeterminado para la detección automática (si el idioma del usuario no es compatible con el bot) se puede configurar utilizando la variable `AUTO_LANG`. El idioma predeterminado es el inglés (`en`). Este idioma predeterminado se utiliza para los errores del bot o algunos mensajes de depuración.

### Soporte de proxy

El bot admite el uso de un proxy solo para las solicitudes de la API. Para utilizar un proxy, proporciona la URL del proxy en la variable `API_TUNNEL` (por ejemplo, `http://127.0.0.1:3128`). Si no se necesita un proxy, deja esta variable vacía.
## Configuration

### Telegram Token

To use the Telegram bot, you need to provide a Telegram token. This token can be obtained by creating a bot via `https://t.me/botfather`. The token needs to be stored in the `TELEGRAM_TOKEN` environment variable.

### Menu Configuration

The bot's menu can be configured with the following options:

- `MAX_ITEMS_PER_PAGE`: The maximum number of items to display per page in the menu. Default is 10.
- `MAX_COLUMNS_PER_PAGE`: The maximum number of columns to display per page in the menu. Default is 2.

### User and Chat Whitelist

You can specify a whitelist of users and chats that are allowed to interact with the bot. The whitelist should be provided as a list of user or chat IDs in the `USER_WHITELIST` and `CHAT_WHITELIST` environment variables, respectively.

### Database Configuration

The bot supports both MongoDB and JSON database options. By default, it uses Mongo database. To use JSON Database, set the `WITHOUT_MONGODB` environment variable to `True`.

### Dialog Timeout

The bot has a dialog timeout feature, which automatically ends a conversation if there is no activity for a certain period of time. The timeout duration can be configured using the `DIALOG_TIMEOUT` environment variable. The default timeout is 7200 seconds (2 hours).

### Image Generation

The bot can generate images based on user input. The number of images to generate can be configured using the `OUTPUT_IMAGES` environment variable. The default is 4 images.

### URL Direct Response

By default, the bot answers after sending a URL to be read. To disable this and wait to the user input after processing the url, set the `URL_DIRECT_RESPONSE` environment variable to `False`.

### Streaming Answers

The bot answers with streaming responses, which allows for continuous output of results. To disable this feature, set the `STREAM_ANSWERS` environment variable to `False`.

### Function Calls

The bot supports new OpenAI function calls. To disable this feature, set the `FEATURE_FUNCTION_CALLS` environment variable to `False`.

### Timeout Ask

The bot has a feature for asking if continue or start a new conversation. If disabled, the bot will automatically remove the timeout conversation and start a new one. To disable this feature, set the `TIMEOUT_ASK` environment variable to `False`.

### Transcription

The bot supports transcription of audio files. To disable this feature, set the `FEATURE_TRANSCRIPTION` environment variable to `False`.

### OCR (Optical Character Recognition)

The bot supports OCR for reading text from images. To disable this feature, set the `FEATURE_IMAGE_READ` environment variable to `False`.

### Document Reading

The bot supports reading documents. To disable this feature, set the `FEATURE_DOCUMENT_READ` environment variable to `False`.

### Image Generation

The bot supports generating images based on user input. To disable this feature, set the `FEATURE_IMAGE_GENERATION` environment variable to `False`.

### Web Search

The bot supports web search functionality. To disable this feature, set the `FEATURE_BROWSING` environment variable to `False`.

### URL Reading

The bot supports reading the content of URLs. To disable this feature, set the `FEATURE_URL_READ` environment variable to `False`.

### Audio and File Size Limits

The bot has limits on the size of audio files and documents that can be processed. The maximum audio file size can be configured using the `AUDIO_MAX_MB` environment variable (default is 20MB), and the maximum document file size can be configured using the `DOC_MAX_MB` environment variable (default is 10MB).... ex. AUDIO_MAX_MB=20

### Generated Image Expiration

Generated images have an expiration time after which they are deleted. The expiration time can be configured using the `GENERATED_IMAGE_EXPIRATION_MINUTES` environment variable. The default expiration time is 5 minutes.

### URL Size Limit

The bot has a limit on the size of URLs that can be processed. The maximum URL size can be configured using the `URL_MAX_MB` environment variable. The default limit is 5MB.

### Request Retries and Timeout

The bot supports request retries in case of failures. The maximum number of retries can be configured using the `REQUEST_MAX_RETRIES` environment variable. The default is 3 retries. The request timeout duration can be configured using the `REQUEST_TIMEOUT` environment variable. The default timeout is 10 seconds.

### PDF Page Limit

When reading PDF documents, the bot has a limit on the number of pages that can be processed. The maximum page limit can be configured using the `PDF_PAGE_LIMIT` environment variable. The default limit is 25 pages.

### Automatic Language Detection

The bot supports automatic language detection for context and menus. The default language for automatic detection (if the user language is not supported by the bot) can be configured using the `AUTO_LANG` environment variable. The default language is English (`en`). This default language is used for bot errors or some debug messages

### Proxy Support

The bot supports using a proxy only for API requests. To use a proxy, provide the proxy URL in the `API_TUNNEL` environment variable (ex. `http://127.0.0.1:3128`). If no proxy is needed, leave this variable empty.
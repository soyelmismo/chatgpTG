- Bot: https://t.me/chismegptbpt

[![en](https://img.shields.io/badge/Variables-en-brightgreen)](https://gg.resisto.rodeo/yo/chatgpTG/src/branch/main/docs/variables/en.md)

## Commands:
- /new - Start a new dialogue.
- /img - Generate images.
- /retry - Regenerate the bot's last response.
- /chat_mode - Select the chat mode.
- /model - Show AI models.
- /api - Show APIs.
- /lang - View available languages.
- /status - View current configuration: Model, Chat mode, and API.
- /reset - Reset configuration to default values.
- /search - Search on the internet.
- /help - Show this message again.

## Features:
- Function calls! (plugins connected directly to GPT, June models>).
- Local JSON database.
- Highly modular and customizable.
- Make GPT access the internet using /search!
- Send a text file, PDF, or URL and the bot will analyze them!
- Add reverse proxies from OpenAI and their respective models as much as you want!
- Multi-language.
- Read text from images.
- Transcribe audios.

# Important:
- Custom APIs must follow the same structure as OpenAI, i.e., "https://domain.dom/v1/..."

## Setup
1. Get your [OpenAI API](https://openai.com/api/) key.

2. Get your Telegram bot token from [@BotFather](https://t.me/BotFather).

3. Edit `config/api.example.json` to configure your API key or add custom APIs.

4. Add your Telegram token, MongoDB database, modify other variables in 'docker-compose.example.yml', and rename `docker-compose.example.yml` to `docker-compose.yml`.

5. 🔥 Access the directory from the terminal and **run**:
    ```bash
    docker-compose up --build
    ```
# Star History

<a href="https://gg.resisto.rodeo/yo/chatgpTG"><img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=soyelmismo/chatgpTG&type=Date"></a> 

## References
1. Original: <a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>
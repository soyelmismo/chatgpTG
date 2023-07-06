- Bot: https://t.me/chismegptbpt

[![nl](https://img.shields.io/badge/Variabelen-nl-red)](https://gg.resisto.rodeo/yo/chatgpTG/src/branch/main/docs/variables/nl.md)

## Opdrachten:
- /new - Start een nieuw gesprek.
- /img - Genereer afbeeldingen.
- /retry - Genereer het laatste antwoord opnieuw.
- /chat_mode - Selecteer de gespreksmodus.
- /model - Toon AI-modellen.
- /api - Toon API's.
- /lang - Bekijk beschikbare talen.
- /status - Bekijk de huidige configuratie: Model, Chatmodus en API.
- /reset - Herstel de instellingen naar de standaardwaarden.
- /search - Zoek op internet.
- /help - Toon dit bericht opnieuw.

## Kenmerken:
- Functieoproepen! (plugins direct verbonden met GPT, modellen van juni>).
- Lokale JSON-database.
- Zeer modulair en aanpasbaar.
- Laat GPT toegang krijgen tot internet met /search!
- Stuur een tekstbestand, PDF of URL en de bot kan ze analyseren!
- Voeg zoveel omgekeerde proxies van OpenAI toe als je wilt!
- Meertalig.
- Lees tekst van afbeeldingen.
- Transcribeer audio.

# Belangrijk:
- Aangepaste API's moeten dezelfde structuur volgen als OpenAI, dwz "https://domain.dom/v1/..."

## Installatie
1. Verkrijg uw [OpenAI API-sleutel](https://openai.com/api/)

2. Verkrijg uw Telegram-bot-token van [@BotFather](https://t.me/BotFather)

3. Bewerk `config/api.example.json` om uw API-KEY te configureren of aangepaste API's toe te voegen

4. Voeg uw Telegram-token toe, MongoDB-database, wijzig andere variabelen in 'docker-compose.example.yml' en hernoem `docker-compose.example.yml` naar `docker-compose.yml`

5. 🔥 Ga naar de map in de terminal en **voer uit**:
    ```bash
    docker-compose up --build
    ```
# Stergeschiedenis

<a href="https://gg.resisto.rodeo/yo/chatgpTG"><img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=soyelmismo/chatgpTG&type=Date"></a> 

## Referenties
1. Oorsprong: <a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>
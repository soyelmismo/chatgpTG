- Bot: https://t.me/chismegptbpt

[![de](https://img.shields.io/badge/Variablen-de-blue)](https://gg.resisto.rodeo/yo/chatgpTG/src/branch/main/docs/variables/de.md)

## Befehle:
- /new - Starten Sie einen neuen Dialog.
- /img - Generieren Sie Bilder.
- /retry - Generieren Sie die letzte Antwort des Bots erneut.
- /chat_mode - Wählen Sie den Chat-Modus aus.
- /model - Zeigen Sie KI-Modelle an.
- /api - Zeigen Sie APIs an.
- /lang - Verfügbar Sprachen anzeigen.
- /status - Aktuelle Konfiguration anzeigen: Modell, Chat-Modus und API.
- /reset - Setzen Sie die Konfiguration auf die Standardeinstellungen zurück.
- /search - Suche im Internet
- /help - Zeigen Sie diese Nachricht erneut an.

## Eigenschaften:
- Aufruf von Funktionen! (Plugins direkt mit GPT verbunden, Modelle ab Juni>).
- Lokale JSON-Datenbank.
- Sehr modular und anpassbar.
- Lassen Sie GPT mit /search auf das Internet zugreifen!
- Senden Sie eine Textdatei, PDF oder URL, und der Bot kann sie analysieren!
- Fügen Sie Reverse-Proxies von OpenAI und ihren entsprechenden Modellen hinzu, so viele Sie möchten!
- Mehrsprachig.
- Liest den Text von Bildern.
- Transkribiert Audios.

# Wichtig:
- Benutzerdefinierte APIs müssen der gleichen Struktur wie OpenAI folgen, d.h. "https://domain.dom/v1/..."

## Einrichtung
1. Holen Sie sich Ihren Schlüssel von [OpenAI API](https://openai.com/api/)

2. Holen Sie sich Ihren Telegramm-Bot-Token von [@BotFather](https://t.me/BotFather)

3. Bearbeiten Sie `config/api.example.json`, um Ihren API-Schlüssel zu konfigurieren oder benutzerdefinierte APIs hinzuzufügen

4. Fügen Sie Ihren Telegramm-Token, Ihre MongoDB-Datenbank hinzu und ändern Sie andere Variablen in 'docker-compose.example.yml' und benennen Sie `docker-compose.example.yml` in `docker-compose.yml` um

5. 🔥 Gehen Sie über das Terminal zum Verzeichnis und **führen Sie** aus:
    ```bash
    docker-compose up --build
    ```
# Sterneverlauf

<a href="https://gg.resisto.rodeo/yo/chatgpTG"><img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=soyelmismo/chatgpTG&type=Date"></a> 

## Referenzen
1. Ursprung: <a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>
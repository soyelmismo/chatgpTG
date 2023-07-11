- Bot: https://t.me/chismegptbpt

[![it](https://img.shields.io/badge/Variabili-it-yellow)](https://gg.resisto.rodeo/yo/chatgpTG/src/branch/main/docs/variables/it.md)

## Comandi:
- /new - Avvia una nuova conversazione.
- /img - Genera immagini.
- /retry - Rigenera l'ultima risposta del bot.
- /chat_mode - Seleziona la modalità di conversazione.
- /model - Mostra i modelli di IA disponibili.
- /api - Mostra le API disponibili.
- /lang - Visualizza le lingue disponibili.
- /status - Visualizza la configurazione attuale: Modello, Modalità di chat e API.
- /reset - Ripristina la configurazione ai valori predefiniti.
- /search - Ricerca su Internet.
- /help - Mostra nuovamente questo messaggio.

## Caratteristiche:
- Chiamata a funzioni! (plugin collegati direttamente a GPT, modelli di giugno>).
- Database JSON locale.
- Estremamente modulare e personalizzabile.
- Permette a GPT di accedere a Internet utilizzando /search!
- Invia un file di testo, PDF o URL e il bot sarà in grado di analizzarlo!
- Aggiungi proxy inversi di OpenAI e relativi modelli a volontà!
- Multilingue.
- Legge il testo dalle immagini.
- Trascrive gli audio.

# Importante:
- Le API personalizzate devono seguire la stessa struttura di OpenAI, cioè "https://dominio.dom/v1/..."

## Configurazione
1. Ottieni la tua chiave API da [OpenAI API](https://openai.com/api/)

2. Ottieni il token del tuo bot Telegram da [@BotFather](https://t.me/BotFather)

3. Modifica `config/api.example.json` per configurare la tua API-KEY o aggiungere API personalizzate

4. Aggiungi il tuo token Telegram, il database Mongo, modifica altre variabili in 'docker-compose.example.yml' e rinomina `docker-compose.example.yml` in `docker-compose.yml`

5. 🔥 Accedi alla directory tramite terminale ed **esegui**:
    ```bash
    docker-compose up --build
    ```
# Cronologia delle stelle

<a href="https://gg.resisto.rodeo/yo/chatgpTG"><img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=soyelmismo/chatgpTG&type=Date"></a> 

## Riferimenti
1. Origine: <a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>
## Configuratie

### Telegram Token

Om de Telegram-bot te gebruiken, moet je een Telegram-token verstrekken. Deze token kan worden verkregen door een bot aan te maken via `https://t.me/botfather`. De token moet worden opgeslagen in de variabele `TELEGRAM_TOKEN`.

### Menuconfiguratie

Het menu van de bot kan worden geconfigureerd met de volgende opties:

- `MAX_ITEMS_PER_PAGE`: Het maximale aantal items dat per pagina in het menu wordt weergegeven. Standaard is dit 10.
- `MAX_COLUMNS_PER_PAGE`: Het maximale aantal kolommen dat per pagina in het menu wordt weergegeven. Standaard is dit 2.

### Whitelist voor gebruikers en chats

Je kunt een whitelist van gebruikers en chats specificeren die toegestaan zijn om met de bot te communiceren. De whitelist moet worden opgegeven als een lijst met gebruikers- of chat-ID's in de variabelen `USER_WHITELIST` en `CHAT_WHITELIST`.

### Databaseconfiguratie

De bot ondersteunt zowel MongoDB als JSON-databaseopties. Standaard maakt hij gebruik van de Mongo-database. Om de JSON-database te gebruiken, stel je de variabele `WITHOUT_MONGODB` in op `True`.

### Time-out voor dialoog

De bot heeft een functie voor time-out van de dialoog, waarmee een gesprek automatisch wordt beëindigd als er gedurende een bepaalde periode geen activiteit is. De time-outduur kan worden geconfigureerd met behulp van de variabele `DIALOG_TIMEOUT`. De standaard time-out is 7200 seconden (2 uur).

### Genereren van afbeeldingen

De bot ondersteunt het genereren van afbeeldingen op basis van gebruikersinvoer. Om deze functie uit te schakelen, stel je de variabele `FEATURE_IMAGE_GENERATION` in op `False`.

Het aantal te genereren afbeeldingen kan worden geconfigureerd met behulp van de variabele `OUTPUT_IMAGES`. Standaard worden er 4 afbeeldingen gegenereerd.

Gegenereerde afbeeldingen hebben een vervaltijd waarin ze uit het geheugen van de bot worden verwijderd. De vervaltijd kan worden geconfigureerd met behulp van de variabele `GENERATED_IMAGE_EXPIRATION_MINUTES`. De standaard vervaltijd is 5 minuten.

### Directe respons op URL's

Standaard antwoordt de bot nadat hij een URL heeft verzonden om te lezen. Om dit uit te schakelen en te wachten op de invoer van de gebruiker na het verwerken van de URL, stel je de variabele `URL_DIRECT_RESPONSE` in op `False`.

### Streaming-antwoorden

De bot geeft antwoord met streaming-antwoorden, wat zorgt voor een continue uitvoer van resultaten. Om deze functie uit te schakelen, stel je de variabele `STREAM_ANSWERS` in op `False`.

### Functieoproepen

De bot ondersteunt nieuwe OpenAI-functieoproepen. Om deze functie uit te schakelen, stel je de variabele `FEATURE_FUNCTION_CALLS` in op `False`.

### Time-out vragen

De bot heeft een functie om te vragen of het gesprek moet worden voortgezet of een nieuw gesprek moet worden gestart. Als dit is uitgeschakeld, verwijdert de bot automatisch het time-outgesprek en start een nieuw gesprek. Om deze functie uit te schakelen, stel je de variabele `TIMEOUT_ASK` in op `False`.

### Transcriptie

De bot ondersteunt transcriptie van audiobestanden. Om deze functie uit te schakelen, stel je de variabele `FEATURE_TRANSCRIPTION` in op `False`.

### OCR (Optical Character Recognition)

De bot ondersteunt OCR voor het lezen van tekst uit afbeeldingen. Om deze functie uit te schakelen, stel je de variabele `FEATURE_IMAGE_READ` in op `False`.

### Documentlezen

De bot ondersteunt het lezen van documenten. Om deze functie uit te schakelen, stel je de variabele `FEATURE_DOCUMENT_READ` in op `False`.

### Webscannen

De bot ondersteunt functionaliteit voor webscannen. Om deze functie uit te schakelen, stel je de variabele `FEATURE_BROWSING` in op `False`.

### URL-lezen

De bot ondersteunt het lezen van de inhoud van URL's. Om deze functie uit te schakelen, stel je de variabele `FEATURE_URL_READ` in op `False`.

### Beperkingen voor audio- en bestandsgrootte

De bot heeft beperkingen voor de grootte van audiobestanden en documenten die kunnen worden verwerkt. De maximale grootte van audiobestanden kan worden geconfigureerd met behulp van de variabele `AUDIO_MAX_MB` (standaard is dit 20 MB), en de maximale grootte van documentbestanden kan worden geconfigureerd met behulp van de variabele `DOC_MAX_MB` (standaard is dit 10 MB).... ex. AUDIO_MAX_MB=20

### Beperking voor URL-grootte

De bot heeft een beperking voor de grootte van URL's die kunnen worden verwerkt. De maximale URL-grootte kan worden geconfigureerd met behulp van de variabele `URL_MAX_MB`. De standaardlimiet is 5 MB.

### Herhaalde verzoeken en time-out

De bot ondersteunt herhaalde verzoeken in geval van fouten. Het maximale aantal herhalingen kan worden geconfigureerd met behulp van de variabele `REQUEST_MAX_RETRIES`. Standaard zijn er 3 herhalingen. De time-outduur voor verzoeken kan worden geconfigureerd met behulp van de variabele `REQUEST_TIMEOUT`. De standaard time-out is 10 seconden.

### PDF-paginalimiet

Bij het lezen van PDF-documenten heeft de bot een limiet voor het aantal pagina's dat kan worden verwerkt. Het maximale paginalimiet kan worden geconfigureerd met behulp van de variabele `PDF_PAGE_LIMIT`. De standaardlimiet is 25 pagina's.

### Automatische taaldetectie

De bot ondersteunt automatische taaldetectie voor context en menu's. De standaardtaal voor automatische detectie (als de taal van de gebruiker niet wordt ondersteund door de bot) kan worden geconfigureerd met behulp van de variabele `AUTO_LANG`. De standaardtaal is Engels (`en`). Deze standaardtaal wordt gebruikt voor fouten van de bot of sommige debugberichten.

### Proxy-ondersteuning

De bot ondersteunt alleen het gebruik van een proxy voor API-verzoeken. Om een proxy te gebruiken, verstrek je de proxy-URL in de variabele `API_TUNNEL` (bijv. `http://127.0.0.1:3128`). Als er geen proxy nodig is, laat je deze variabele leeg.
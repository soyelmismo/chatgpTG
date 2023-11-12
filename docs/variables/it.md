## Configurazione

### Token di Telegram

Per utilizzare il bot di Telegram, è necessario fornire un token di Telegram. Questo token può essere ottenuto creando un bot tramite `https://t.me/botfather`. Il token deve essere memorizzato nella variabile `TELEGRAM_TOKEN`.

### Configurazione del menu

Il menu del bot può essere configurato con le seguenti opzioni:

- `MAX_ITEMS_PER_PAGE`: Il numero massimo di elementi da visualizzare per pagina nel menu. Il valore predefinito è 10.
- `MAX_COLUMNS_PER_PAGE`: Il numero massimo di colonne da visualizzare per pagina nel menu. Il valore predefinito è 2.

### Whitelist di utenti e chat

È possibile specificare una whitelist di utenti e chat che sono autorizzati a interagire con il bot. La whitelist deve essere fornita come una lista di ID utente o chat nelle variabili `USER_WHITELIST`, rispettivamente.

### Configurazione del database

Il bot supporta sia MongoDB che JSON come opzioni di database. Per impostazione predefinita, utilizza il database Mongo. Per utilizzare il database JSON, impostare la variabile `WITHOUT_MONGODB` su `True`.

### Timeout del dialogo

Il bot dispone di una funzione di timeout del dialogo, che termina automaticamente una conversazione se non vi è attività per un certo periodo di tempo. La durata del timeout può essere configurata utilizzando la variabile `DIALOG_TIMEOUT`. Il timeout predefinito è di 7200 secondi (2 ore).

### Generazione di immagini

Il bot supporta la generazione di immagini in base all'input dell'utente. Per disabilitare questa funzione, impostare la variabile `FEATURE_IMAGE_GENERATION` su `False`.

Il numero di immagini da generare può essere configurato utilizzando la variabile `OUTPUT_IMAGES`. Il valore predefinito è di 4 immagini.

Le immagini generate hanno un tempo di scadenza dopo il quale vengono eliminate dalla memoria del bot. Il tempo di scadenza può essere configurato utilizzando la variabile `GENERATED_IMAGE_EXPIRATION_MINUTES`. Il tempo di scadenza predefinito è di 5 minuti.

### Risposta diretta all'URL

Per impostazione predefinita, il bot risponde dopo aver inviato un URL da leggere. Per disabilitare questa funzione e attendere l'input dell'utente dopo l'elaborazione dell'URL, impostare la variabile `URL_DIRECT_RESPONSE` su `False`.

### Risposte in streaming

Il bot risponde con risposte in streaming, che consentono un output continuo dei risultati. Per disabilitare questa funzione, impostare la variabile `STREAM_ANSWERS` su `False`.

### Chiamate di funzione

Il bot supporta nuove chiamate di funzione di OpenAI. Per disabilitare questa funzione, impostare la variabile `FEATURE_FUNCTION_CALLS` su `False`.

### Timeout di richiesta

Il bot dispone di una funzione per chiedere se continuare o avviare una nuova conversazione. Se disabilitato, il bot rimuoverà automaticamente la conversazione in timeout e ne avvierà una nuova. Per disabilitare questa funzione, impostare la variabile `TIMEOUT_ASK` su `False`.

### Trascrizione

Il bot supporta la trascrizione dei file audio. Per disabilitare questa funzione, impostare la variabile `FEATURE_TRANSCRIPTION` su `False`.

### OCR (Riconoscimento ottico dei caratteri)

Il bot supporta l'OCR per leggere il testo dalle immagini. Per disabilitare questa funzione, impostare la variabile `FEATURE_IMAGE_READ` su `False`.

### Lettura dei documenti

Il bot supporta la lettura dei documenti. Per disabilitare questa funzione, impostare la variabile `FEATURE_DOCUMENT_READ` su `False`.

### Ricerca web

Il bot supporta la funzionalità di ricerca web. Per disabilitare questa funzione, impostare la variabile `FEATURE_BROWSING` su `False`.

### Lettura degli URL

Il bot supporta la lettura del contenuto degli URL. Per disabilitare questa funzione, impostare la variabile `FEATURE_URL_READ` su `False`.

### Limiti di dimensione audio e file

Il bot ha limiti sulla dimensione dei file audio e dei documenti che possono essere elaborati. La dimensione massima del file audio può essere configurata utilizzando la variabile `AUDIO_MAX_MB` (il valore predefinito è di 20 MB), e la dimensione massima del file del documento può essere configurata utilizzando la variabile `DOC_MAX_MB` (il valore predefinito è di 10 MB).... es. AUDIO_MAX_MB=20

### Limite di dimensione degli URL

Il bot ha un limite sulla dimensione degli URL che possono essere elaborati. Il limite massimo della dimensione dell'URL può essere configurato utilizzando la variabile `URL_MAX_MB`. Il limite predefinito è di 5 MB.

### Ritentativi e timeout delle richieste

Il bot supporta i ritentativi delle richieste in caso di errori. Il numero massimo di ritentativi può essere configurato utilizzando la variabile `REQUEST_MAX_RETRIES`. Il valore predefinito è di 3 ritentativi. La durata del timeout della richiesta può essere configurata utilizzando la variabile `REQUEST_TIMEOUT`. Il timeout predefinito è di 10 secondi.

### Limite di pagine PDF

Quando si leggono documenti PDF, il bot ha un limite sul numero di pagine che possono essere elaborate. Il limite massimo di pagine può essere configurato utilizzando la variabile `PDF_PAGE_LIMIT`. Il limite predefinito è di 25 pagine.

### Rilevamento automatico della lingua

Il bot supporta il rilevamento automatico della lingua per il contesto e i menu. La lingua predefinita per il rilevamento automatico (se la lingua dell'utente non è supportata dal bot) può essere configurata utilizzando la variabile `AUTO_LANG`. La lingua predefinita è l'inglese (`en`). Questa lingua predefinita viene utilizzata per gli errori del bot o alcuni messaggi di debug.

### Supporto del proxy

Il bot supporta l'utilizzo di un proxy solo per le richieste API. Per utilizzare un proxy, fornire l'URL del proxy nella variabile `API_TUNNEL` (ad esempio `http://127.0.0.1:3128`). Se non è necessario un proxy, lasciare questa variabile vuota.
## Konfiguration

### Telegram-Token

Um den Telegram-Bot zu verwenden, müssen Sie ein Telegram-Token bereitstellen. Dieses Token kann erhalten werden, indem Sie einen Bot über `https://t.me/botfather` erstellen. Das Token muss in der Variablen `TELEGRAM_TOKEN` gespeichert werden.

### Menükonfiguration

Das Menü des Bots kann mit den folgenden Optionen konfiguriert werden:

- `MAX_ITEMS_PER_PAGE`: Die maximale Anzahl von Elementen, die pro Seite im Menü angezeigt werden sollen. Standardmäßig sind es 10.
- `MAX_COLUMNS_PER_PAGE`: Die maximale Anzahl von Spalten, die pro Seite im Menü angezeigt werden sollen. Standardmäßig sind es 2.

### Benutzer- und Chat-Whitelist

Sie können eine Whitelist von Benutzern und Chats angeben, die mit dem Bot interagieren dürfen. Die Whitelist sollte als Liste von Benutzer- oder Chat-IDs in den Variablen `USER_WHITELIST` bzw. `CHAT_WHITELIST` angegeben werden.

### Datenbankkonfiguration

Der Bot unterstützt sowohl MongoDB- als auch JSON-Datenbankoptionen. Standardmäßig verwendet er die Mongo-Datenbank. Um die JSON-Datenbank zu verwenden, setzen Sie die Variable `WITHOUT_MONGODB` auf `True`.

### Dialog-Timeout

Der Bot verfügt über eine Funktion zum Timeout von Dialogen, die ein Gespräch automatisch beendet, wenn für eine bestimmte Zeit keine Aktivität stattfindet. Die Timeout-Dauer kann mit der Variable `DIALOG_TIMEOUT` konfiguriert werden. Der Standard-Timeout beträgt 7200 Sekunden (2 Stunden).

### Bildgenerierung

Der Bot unterstützt die Generierung von Bildern basierend auf Benutzereingaben. Um diese Funktion zu deaktivieren, setzen Sie die Variable `FEATURE_IMAGE_GENERATION` auf `False`.

Die Anzahl der zu generierenden Bilder kann mit der Variable `OUTPUT_IMAGES` konfiguriert werden. Standardmäßig werden 4 Bilder generiert.

Generierte Bilder haben eine Ablaufzeit, nach der sie aus dem Speicher des Bots gelöscht werden. Die Ablaufzeit kann mit der Variable `GENERATED_IMAGE_EXPIRATION_MINUTES` konfiguriert werden. Die Standard-Ablaufzeit beträgt 5 Minuten.

### Direkte Antwort auf URLs

Standardmäßig antwortet der Bot, nachdem er eine URL zum Lesen gesendet hat. Um dies zu deaktivieren und auf die Benutzereingabe nach der Verarbeitung der URL zu warten, setzen Sie die Variable `URL_DIRECT_RESPONSE` auf `False`.

### Streaming-Antworten

Der Bot antwortet mit Streaming-Antworten, die eine kontinuierliche Ausgabe von Ergebnissen ermöglichen. Um diese Funktion zu deaktivieren, setzen Sie die Variable `STREAM_ANSWERS` auf `False`.

### Funktionsaufrufe

Der Bot unterstützt neue OpenAI-Funktionsaufrufe. Um diese Funktion zu deaktivieren, setzen Sie die Variable `FEATURE_FUNCTION_CALLS` auf `False`.

### Timeout-Frage

Der Bot verfügt über eine Funktion, um zu fragen, ob das Gespräch fortgesetzt oder ein neues Gespräch gestartet werden soll. Wenn diese Funktion deaktiviert ist, entfernt der Bot automatisch das Timeout-Gespräch und startet ein neues. Um diese Funktion zu deaktivieren, setzen Sie die Variable `TIMEOUT_ASK` auf `False`.

### Transkription

Der Bot unterstützt die Transkription von Audiodateien. Um diese Funktion zu deaktivieren, setzen Sie die Variable `FEATURE_TRANSCRIPTION` auf `False`.

### OCR (Optische Zeichenerkennung)

Der Bot unterstützt OCR zum Lesen von Texten aus Bildern. Um diese Funktion zu deaktivieren, setzen Sie die Variable `FEATURE_IMAGE_READ` auf `False`.

### Dokumentenlesen

Der Bot unterstützt das Lesen von Dokumenten. Um diese Funktion zu deaktivieren, setzen Sie die Variable `FEATURE_DOCUMENT_READ` auf `False`.

### Websuche

Der Bot unterstützt die Funktion zur Websuche. Um diese Funktion zu deaktivieren, setzen Sie die Variable `FEATURE_BROWSING` auf `False`.

### URL-Lesen

Der Bot unterstützt das Lesen des Inhalts von URLs. Um diese Funktion zu deaktivieren, setzen Sie die Variable `FEATURE_URL_READ` auf `False`.

### Audio- und Dateigrößenbeschränkungen

Der Bot hat Beschränkungen für die Größe von Audiodateien und Dokumenten, die verarbeitet werden können. Die maximale Größe der Audiodatei kann mit der Variable `AUDIO_MAX_MB` konfiguriert werden (Standardwert sind 20 MB), und die maximale Größe der Dokumentendatei kann mit der Variable `DOC_MAX_MB` konfiguriert werden (Standardwert sind 10 MB).... z.B. AUDIO_MAX_MB=20

### URL-Größenbeschränkung

Der Bot hat eine Beschränkung für die Größe von URLs, die verarbeitet werden können. Die maximale URL-Größe kann mit der Variable `URL_MAX_MB` konfiguriert werden. Die Standardgrenze beträgt 5 MB.

### Anfrage-Wiederholungen und Timeout

Der Bot unterstützt Anfrage-Wiederholungen im Falle von Fehlern. Die maximale Anzahl von Wiederholungen kann mit der Variable `REQUEST_MAX_RETRIES` konfiguriert werden. Standardmäßig sind es 3 Wiederholungen. Die Timeout-Dauer für Anfragen kann mit der Variable `REQUEST_TIMEOUT` konfiguriert werden. Das Standard-Timeout beträgt 10 Sekunden.

### PDF-Seitenlimit

Beim Lesen von PDF-Dokumenten hat der Bot eine Begrenzung für die Anzahl der Seiten, die verarbeitet werden können. Das maximale Seitenlimit kann mit der Variable `PDF_PAGE_LIMIT` konfiguriert werden. Das Standardlimit beträgt 25 Seiten.

### Automatische Spracherkennung

Der Bot unterstützt die automatische Spracherkennung für Kontext und Menüs. Die Standardsprache für die automatische Erkennung (wenn die Benutzersprache vom Bot nicht unterstützt wird) kann mit der Variable `AUTO_LANG` konfiguriert werden. Die Standardsprache ist Englisch (`en`). Diese Standardsprache wird für Bot-Fehler oder einige Debug-Nachrichten verwendet.

### Proxy-Unterstützung

Der Bot unterstützt die Verwendung eines Proxys nur für API-Anfragen. Um einen Proxy zu verwenden, geben Sie die Proxy-URL in der Variable `API_TUNNEL` an (z.B. `http://127.0.0.1:3128`). Wenn kein Proxy benötigt wird, lassen Sie diese Variable leer.
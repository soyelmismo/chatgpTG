## Configuration

### Jeton Telegram

Pour utiliser le bot Telegram, vous devez fournir un jeton Telegram. Ce jeton peut être obtenu en créant un bot via `https://t.me/botfather`. Le jeton doit être stocké dans la variable `TELEGRAM_TOKEN`.

### Configuration du menu

Le menu du bot peut être configuré avec les options suivantes :

- `MAX_ITEMS_PER_PAGE` : Le nombre maximum d'éléments à afficher par page dans le menu. Par défaut, il est de 10.
- `MAX_COLUMNS_PER_PAGE` : Le nombre maximum de colonnes à afficher par page dans le menu. Par défaut, il est de 2.

### Liste blanche des utilisateurs et des discussions

Vous pouvez spécifier une liste blanche des utilisateurs et des discussions autorisés à interagir avec le bot. La liste blanche doit être fournie sous la forme d'une liste d'identifiants d'utilisateurs ou de discussions dans les variables `USER_WHITELIST` et `CHAT_WHITELIST`, respectivement.

### Configuration de la base de données

Le bot prend en charge les options de base de données MongoDB et JSON. Par défaut, il utilise la base de données Mongo. Pour utiliser la base de données JSON, définissez la variable `WITHOUT_MONGODB` sur `True`.

### Délai d'attente du dialogue

Le bot dispose d'une fonction de délai d'attente du dialogue, qui met fin automatiquement à une conversation s'il n'y a aucune activité pendant une certaine période de temps. La durée du délai d'attente peut être configurée à l'aide de la variable `DIALOG_TIMEOUT`. Le délai d'attente par défaut est de 7200 secondes (2 heures).

### Génération d'images

Le bot prend en charge la génération d'images en fonction de la saisie de l'utilisateur. Pour désactiver cette fonctionnalité, définissez la variable `FEATURE_IMAGE_GENERATION` sur `False`.

Le nombre d'images à générer peut être configuré à l'aide de la variable `OUTPUT_IMAGES`. Par défaut, il y a 4 images.

Les images générées ont une durée de validité après laquelle elles sont supprimées de la mémoire du bot. La durée de validité peut être configurée à l'aide de la variable `GENERATED_IMAGE_EXPIRATION_MINUTES`. La durée de validité par défaut est de 5 minutes.

### Réponse directe à l'URL

Par défaut, le bot répond après avoir envoyé une URL à lire. Pour désactiver cela et attendre la saisie de l'utilisateur après le traitement de l'URL, définissez la variable `URL_DIRECT_RESPONSE` sur `False`.

### Réponses en continu

Le bot répond avec des réponses en continu, ce qui permet une sortie continue des résultats. Pour désactiver cette fonctionnalité, définissez la variable `STREAM_ANSWERS` sur `False`.

### Appels de fonctions

Le bot prend en charge de nouveaux appels de fonctions OpenAI. Pour désactiver cette fonctionnalité, définissez la variable `FEATURE_FUNCTION_CALLS` sur `False`.

### Demande de délai d'attente

Le bot dispose d'une fonctionnalité pour demander s'il faut continuer ou commencer une nouvelle conversation. Si elle est désactivée, le bot supprimera automatiquement la conversation en attente et en démarrera une nouvelle. Pour désactiver cette fonctionnalité, définissez la variable `TIMEOUT_ASK` sur `False`.

### Transcription

Le bot prend en charge la transcription des fichiers audio. Pour désactiver cette fonctionnalité, définissez la variable `FEATURE_TRANSCRIPTION` sur `False`.

### OCR (Reconnaissance optique de caractères)

Le bot prend en charge l'OCR pour lire du texte à partir d'images. Pour désactiver cette fonctionnalité, définissez la variable `FEATURE_IMAGE_READ` sur `False`.

### Lecture de documents

Le bot prend en charge la lecture de documents. Pour désactiver cette fonctionnalité, définissez la variable `FEATURE_DOCUMENT_READ` sur `False`.

### Recherche Web

Le bot prend en charge la fonctionnalité de recherche Web. Pour désactiver cette fonctionnalité, définissez la variable `FEATURE_BROWSING` sur `False`.

### Lecture d'URL

Le bot prend en charge la lecture du contenu des URL. Pour désactiver cette fonctionnalité, définissez la variable `FEATURE_URL_READ` sur `False`.

### Limites de taille des fichiers audio et des documents

Le bot impose des limites sur la taille des fichiers audio et des documents pouvant être traités. La taille maximale des fichiers audio peut être configurée à l'aide de la variable `AUDIO_MAX_MB` (par défaut, elle est de 20 Mo), et la taille maximale des fichiers de documents peut être configurée à l'aide de la variable `DOC_MAX_MB` (par défaut, elle est de 10 Mo).... ex. AUDIO_MAX_MB=20

### Limite de taille des URL

Le bot impose une limite sur la taille des URL pouvant être traitées. La taille maximale des URL peut être configurée à l'aide de la variable `URL_MAX_MB`. La limite par défaut est de 5 Mo.

### Nouvelles tentatives de demande et délai d'attente

Le bot prend en charge les nouvelles tentatives de demande en cas d'échec. Le nombre maximal de nouvelles tentatives peut être configuré à l'aide de la variable `REQUEST_MAX_RETRIES`. Par défaut, il y a 3 nouvelles tentatives. La durée d'attente de la demande peut être configurée à l'aide de la variable `REQUEST_TIMEOUT`. Le délai d'attente par défaut est de 10 secondes.

### Limite de pages PDF

Lors de la lecture de documents PDF, le bot impose une limite sur le nombre de pages pouvant être traitées. La limite maximale de pages peut être configurée à l'aide de la variable `PDF_PAGE_LIMIT`. La limite par défaut est de 25 pages.

### Détection automatique de la langue

Le bot prend en charge la détection automatique de la langue pour le contexte et les menus. La langue par défaut pour la détection automatique (si la langue de l'utilisateur n'est pas prise en charge par le bot) peut être configurée à l'aide de la variable `AUTO_LANG`. La langue par défaut est l'anglais (`en`). Cette langue par défaut est utilisée pour les erreurs du bot ou certains messages de débogage.

### Prise en charge des proxys

Le bot prend en charge l'utilisation d'un proxy uniquement pour les demandes d'API. Pour utiliser un proxy, fournissez l'URL du proxy dans la variable `API_TUNNEL` (ex. `http://127.0.0.1:3128`). Si aucun proxy n'est nécessaire, laissez cette variable vide.
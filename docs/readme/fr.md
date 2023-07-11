- Bot: https://t.me/chismegptbpt

[![fr](https://img.shields.io/badge/Variables-fr-brightgreen)](https://gg.resisto.rodeo/yo/chatgpTG/src/branch/main/docs/variables/fr.md)

## Commandes:
- /new - Démarrer une nouvelle conversation.
- /img - Générer des images.
- /retry - Régénère la dernière réponse du bot.
- /chat_mode - Sélectionner le mode de conversation.
- /model - Afficher les modèles d'IA.
- /api - Afficher les APIs.
- /lang - Voir les langues disponibles.
- /status - Voir la configuration actuelle : Modèle, Mode de conversation et API.
- /reset - Rétablir la configuration par défaut.
- /search - Recherche sur Internet.
- /help - Afficher ce message à nouveau.

## Caractéristiques:
- Appel de fonctions ! (plugins connectés directement à GPT, modèles de juin>).
- Base de données JSON locale.
- Très modulaire et personnalisable.
- Permet à GPT d'accéder à Internet en utilisant /search !
- Envoyez un fichier texte, PDF ou une URL et le bot pourra les analyser !
- Ajoutez des proxies inverses d'OpenAI et leurs modèles respectifs autant que vous le souhaitez !
- Multilingue.
- Lit le texte des images.
- Transcrit les fichiers audio.

# Important:
- Les APIs personnalisées doivent suivre la même structure qu'OpenAI, c'est-à-dire "https://domaine.dom/v1/..."

## Configuration
1. Obtenez votre clé d'API [OpenAI](https://openai.com/api/)

2. Obtenez votre jeton de bot Telegram auprès de [@BotFather](https://t.me/BotFather)

3. Modifiez `config/api.example.json` pour configurer votre API-KEY ou ajouter des APIs personnalisées

4. Ajoutez votre jeton Telegram, votre base de données Mongo, modifiez d'autres variables dans 'docker-compose.example.yml' et renommez `docker-compose.example.yml` en `docker-compose.yml`

5. 🔥 Accédez au répertoire depuis le terminal et **exécutez** :
    ```bash
    docker-compose up --build
    ```
# Historique des étoiles

<a href="https://gg.resisto.rodeo/yo/chatgpTG"><img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=soyelmismo/chatgpTG&type=Date"></a> 

## Références
1. Source : <a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>
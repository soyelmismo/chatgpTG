- Bot: https://t.me/chismegptbpt

[![pt](https://img.shields.io/badge/Variáveis-pt-brightgreen)](https://gg.resisto.rodeo/yo/chatgpTG/src/branch/main/docs/variables/pt.md)

## Comandos:
- /new - Iniciar novo diálogo.
- /img - Gerar imagens.
- /retry - Regenerar a última resposta do bot.
- /chat_mode - Selecionar o modo de conversação.
- /model - Mostrar modelos de IA.
- /api - Mostrar APIs.
- /lang - Ver idiomas disponíveis.
- /status - Ver a configuração atual: Modelo, Modo de chat e API.
- /reset - Restaurar a configuração para os valores padrão.
- /search - Pesquisar na internet.
- /help - Mostrar esta mensagem novamente.

## Características:
- Chamada de funções! (plugins conectados diretamente ao GPT, modelos de junho>).
- Banco de dados JSON local.
- Muito modular e personalizável.
- Faça o GPT acessar a internet usando /search!
- Envie um arquivo de texto, PDF ou URL e o bot poderá analisá-los!
- Adicione proxies reversos da OpenAI e seus respectivos modelos quantas vezes quiser!
- Multilíngue.
- Leia o texto de imagens.
- Transcreva áudios.

# Importante:
- As APIs personalizadas devem seguir a mesma estrutura da OpenAI, ou seja, "https://dominio.dom/v1/..."

## Configuração
1. Obtenha sua chave da [OpenAI API](https://openai.com/api/)

2. Obtenha o token do seu bot do Telegram com [@BotFather](https://t.me/BotFather)

3. Edite `config/api.example.json` para configurar sua API-KEY ou adicionar APIs personalizadas

4. Adicione seu token do Telegram, banco de dados Mongo, modifique outras variáveis no arquivo 'docker-compose.example.yml' e renomeie `docker-compose.example.yml` para `docker-compose.yml`

5. 🔥 Acesse o diretório pelo terminal e **execute**:
    ```bash
    docker-compose up --build
    ```
# Histórico de estrelas

<a href="https://gg.resisto.rodeo/yo/chatgpTG"><img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=soyelmismo/chatgpTG&type=Date"></a> 

## Referências
1. Origem: <a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>
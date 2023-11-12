## Configuração

### Token do Telegram

Para usar o bot do Telegram, você precisa fornecer um token do Telegram. Esse token pode ser obtido criando um bot através do `https://t.me/botfather`. O token precisa ser armazenado na variável `TELEGRAM_TOKEN`.

### Configuração do Menu

O menu do bot pode ser configurado com as seguintes opções:

- `MAX_ITEMS_PER_PAGE`: O número máximo de itens a serem exibidos por página no menu. O padrão é 10.
- `MAX_COLUMNS_PER_PAGE`: O número máximo de colunas a serem exibidas por página no menu. O padrão é 2.

### Lista Branca de Usuários e Chats

Você pode especificar uma lista branca de usuários e chats que têm permissão para interagir com o bot. A lista branca deve ser fornecida como uma lista de IDs de usuário ou chat na variávei `USER_WHITELIST`, respectivamente.

### Configuração do Banco de Dados

O bot suporta opções de banco de dados tanto do MongoDB quanto do JSON. Por padrão, ele usa o banco de dados do Mongo. Para usar o banco de dados JSON, defina a variável `WITHOUT_MONGODB` como `True`.

### Tempo Limite do Diálogo

O bot possui uma função de tempo limite de diálogo, que encerra automaticamente uma conversa se não houver atividade por um determinado período de tempo. A duração do tempo limite pode ser configurada usando a variável `DIALOG_TIMEOUT`. O tempo limite padrão é de 7200 segundos (2 horas).

### Geração de Imagens

O bot suporta a geração de imagens com base na entrada do usuário. Para desativar esse recurso, defina a variável `FEATURE_IMAGE_GENERATION` como `False`.

O número de imagens a serem geradas pode ser configurado usando a variável `OUTPUT_IMAGES`. O padrão é de 4 imagens.

As imagens geradas têm um tempo de expiração após o qual são excluídas da memória do bot. O tempo de expiração pode ser configurado usando a variável `GENERATED_IMAGE_EXPIRATION_MINUTES`. O tempo de expiração padrão é de 5 minutos.

### Resposta Direta de URL

Por padrão, o bot responde após enviar uma URL para ser lida. Para desativar isso e aguardar a entrada do usuário após o processamento da URL, defina a variável `URL_DIRECT_RESPONSE` como `False`.

### Respostas em Streaming

O bot responde com respostas em streaming, o que permite a saída contínua de resultados. Para desativar esse recurso, defina a variável `STREAM_ANSWERS` como `False`.

### Chamadas de Função

O bot suporta novas chamadas de função do OpenAI. Para desativar esse recurso, defina a variável `FEATURE_FUNCTION_CALLS` como `False`.

### Pergunta de Tempo Limite

O bot possui uma função para perguntar se deve continuar ou iniciar uma nova conversa. Se desativado, o bot removerá automaticamente a conversa com tempo limite e iniciará uma nova. Para desativar esse recurso, defina a variável `TIMEOUT_ASK` como `False`.

### Transcrição

O bot suporta a transcrição de arquivos de áudio. Para desativar esse recurso, defina a variável `FEATURE_TRANSCRIPTION` como `False`.

### OCR (Reconhecimento Óptico de Caracteres)

O bot suporta OCR para ler texto de imagens. Para desativar esse recurso, defina a variável `FEATURE_IMAGE_READ` como `False`.

### Leitura de Documentos

O bot suporta a leitura de documentos. Para desativar esse recurso, defina a variável `FEATURE_DOCUMENT_READ` como `False`.

### Pesquisa na Web

O bot suporta funcionalidade de pesquisa na web. Para desativar esse recurso, defina a variável `FEATURE_BROWSING` como `False`.

### Leitura de URL

O bot suporta a leitura do conteúdo de URLs. Para desativar esse recurso, defina a variável `FEATURE_URL_READ` como `False`.

### Limites de Tamanho de Áudio e Arquivo

O bot possui limites no tamanho de arquivos de áudio e documentos que podem ser processados. O tamanho máximo do arquivo de áudio pode ser configurado usando a variável `AUDIO_MAX_MB` (o padrão é de 20MB), e o tamanho máximo do arquivo de documento pode ser configurado usando a variável `DOC_MAX_MB` (o padrão é de 10MB).

### Limite de Tamanho de URL

O bot possui um limite no tamanho de URLs que podem ser processados. O tamanho máximo do URL pode ser configurado usando a variável `URL_MAX_MB`. O limite padrão é de 5MB.

### Retentativas e Tempo Limite de Requisição

O bot suporta retentativas de requisição em caso de falhas. O número máximo de retentativas pode ser configurado usando a variável `REQUEST_MAX_RETRIES`. O padrão é de 3 retentativas. A duração do tempo limite da requisição pode ser configurada usando a variável `REQUEST_TIMEOUT`. O tempo limite padrão é de 10 segundos.

### Limite de Páginas de PDF

Ao ler documentos em PDF, o bot possui um limite no número de páginas que podem ser processadas. O limite máximo de páginas pode ser configurado usando a variável `PDF_PAGE_LIMIT`. O limite padrão é de 25 páginas.

### Detecção Automática de Idioma

O bot suporta detecção automática de idioma para contexto e menus. O idioma padrão para detecção automática (se o idioma do usuário não for suportado pelo bot) pode ser configurado usando a variável `AUTO_LANG`. O idioma padrão é o inglês (`en`). Esse idioma padrão é usado para erros do bot ou algumas mensagens de depuração.

### Suporte a Proxy

O bot suporta o uso de um proxy apenas para requisições de API. Para usar um proxy, forneça a URL do proxy na variável `API_TUNNEL` (ex. `http://127.0.0.1:3128`). Se nenhum proxy for necessário, deixe essa variável vazia.
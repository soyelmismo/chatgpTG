from transformers import GPT2Tokenizer, OpenAIGPTTokenizer
from typing import Union, List
#tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')
async def handle(input_data: Union[str, dict, List[dict]], max_tokens):
    buffer_tokens = 500
    max_tokens = int(max_tokens)
    if isinstance(input_data, str): text = input_data
    elif isinstance(input_data, dict): text = " ".join([f"{key}: {value}" for key, value in input_data.items()])
    elif isinstance(input_data, list):
        total_tokens = 0
        for i in range(len(input_data)-1, -1, -1):
            message = input_data[i]
            if message.get("user"):
                tokens = tokenizer.encode(message['user'])
                total_tokens += len(tokens)
            if message.get("bot"):
                tokens = tokenizer.encode(message['bot'])
                total_tokens += len(tokens)
            if message.get("url"):
                tokens = tokenizer.encode(message['url'])
                total_tokens += len(tokens)
            if message.get("documento"):
                tokens = tokenizer.encode(message['documento'])
                total_tokens += len(tokens)
            if message.get("search"):
                tokens = tokenizer.encode(message['search'])
                total_tokens += len(tokens)
            if total_tokens > max_tokens:
                input_data = input_data[i+1:]
                break
        text = '\n'.join([f"{message.get('user', '')} {message.get('bot', '')} {message.get('url', '')} {message.get('documento', '')} {message.get('search', '')}" for message in input_data])
    else: raise ValueError("La entrada debe ser un string, un diccionario o una lista de diccionarios")
    tokens = tokenizer.encode(text)
    # Recortar tokens antiguos si la lista de tokens sobrepasa el límite
    if len(tokens) > max_tokens:
        start_index = len(tokens) - (max_tokens - buffer_tokens)
        tokens = tokens[start_index:]
    if isinstance(input_data, list):
        output_data = []
        token_index = 0
        for item in input_data:
            new_item = {}
            for key, value in item.items():
                if key in ["user", "bot", "search", "documento", "url"]:
                    if value is not None:  # Verifica si el valor no es None
                        content_tokens = tokenizer.encode(value)
                        content_length = len(content_tokens)
                        new_item[key] = tokenizer.decode(content_tokens)
                        token_index += content_length
                    else:
                        pass  # Opcional: asignar un valor predeterminado si el valor es None
                else:
                    new_item[key] = value
            output_data.append(new_item)
        return output_data, token_index
    
    else: return tokenizer.decode(tokens), len(tokens)

from tiktoken import get_encoding
import bot.src.utils.preprocess.remove_words as remove_words
from typing import List, Dict, Any, Tuple

encoding = get_encoding("cl100k_base")

async def handle(input_data: str | List[Dict[str, Any]], max_tokens: int) -> str | List[Dict] | Tuple[int, bool]:
    max_tokens = int(max_tokens)
    try:
        if isinstance(input_data, str):
            tokens = encoding.encode(input_data)
            advertencia=None
            if len(tokens) > max_tokens:
                input_data = await remove_words.handle(texto=input_data)
                tokens = encoding.encode(input_data)
                if len(tokens) > max_tokens:
                    buffer_tokens = 500
                    start_index = len(tokens) - (max_tokens - buffer_tokens)
                    tokens = tokens[start_index:]
                    advertencia = True
            out_tokens = int(len(tokens))
            return str(encoding.decode(tokens)), out_tokens, bool(advertencia)
        elif isinstance(input_data, list):
            output_data, total_tokens, advertencia = await process_input_data(input_data, max_tokens)
            return list(output_data), int(total_tokens), bool(advertencia)
    except Exception as e:
        raise ValueError("tokenizer", {e})

keys = ["user", "bot", "func_cont", "url", "documento", "search"]

async def process_input_data(input_data, max_tokens):
    output_data = []
    total_tokens = 0
    advertencia = None
    for message in input_data:
        new_message, tokens_in_message = await process_message(message, max_tokens)
        
        while total_tokens + tokens_in_message > max_tokens:
            if len(output_data) == 0:
                break
            removed_message = output_data.pop(0)  # Elimina el mensaje más antiguo
            removed_tokens = sum(len(encoding.encode(removed_message[key])) for key in keys if removed_message.get(key))
            total_tokens -= removed_tokens
            advertencia = True

        if total_tokens + tokens_in_message > max_tokens:
            break

        output_data.append(new_message)
        total_tokens += tokens_in_message

    return output_data, total_tokens, advertencia

async def process_message(message, max_tokens):
    total_tokens = 0
    new_message = {}

    for key, value in message.items():
        if key in keys:
            content = str(value)
            tokens = encoding.encode(content)
            content_tokens = len(tokens)
            if total_tokens + content_tokens > max_tokens:
                new_content = await remove_words.handle(texto=content)
                new_tokens = encoding.encode(new_content)
                content_tokens = len(new_tokens)
            else:
                new_content = content
            new_message[key] = str(new_content)
            total_tokens += (content_tokens + 3)
        else:
            new_message[key] = value

    return new_message, total_tokens


async def pre_message(input_data: str) -> int:
    return len(encoding.encode(input_data))

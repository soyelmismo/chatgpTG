import os
import aiohttp
import json
async def create(self):

    messages = self.diccionario["messages"]

    def transform(messages: list) -> list:
        def html_encode(string: str) -> str:
            table = {
                '"': '&quot;',
                "'": '&#39;',
                '&': '&amp;',
                '>': '&gt;',
                '<': '&lt;',
                '\n': '<br>',
                '\t': '&nbsp;&nbsp;&nbsp;&nbsp;',
                ' ': '&nbsp;'
            }

            for key in table:
                string = string.replace(key, table[key])
                
            return string
        
        return [{
            'id': os.urandom(6).hex(),
            'role': message['role'],
            'content': message['content'],
            'who': 'AI: ' if message['role'] == 'assistant' else 'User: ',
            'html': html_encode(message['content'])} for message in messages]
    
    headers = {
        'authority': 'chatgptlogin.ac',
        'accept': '*/*',
        'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
        'content-type': 'application/json',
        'origin': 'https://chatgptlogin.ac',
        'referer': 'https://chatgptai.help/chatgpt-free-use-chat-online/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'x-wp-nonce': "75cfd3c33f"
    }
    
    conversation = transform(messages)

    json_data = {
        'env': 'chatbot',
        'session': 'N/A',
        'prompt': 'Converse as if you were an AI assistant. Be friendly, creative.',
        'context': 'Converse as if you were an AI assistant. Be friendly, creative.',
        'messages': conversation,
        'newMessage': messages[-1]['content'],
        'userName': '<div class="mwai-name-text">User:</div>',
        'aiName': '<div class="mwai-name-text">AI:</div>',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.8,
        'maxTokens': 1024,
        'maxResults': 1,
        'apiKey': '',
        'service': 'openai',
        'embeddingsIndex': '',
        'stop': '',
        'clientId': os.urandom(6).hex()
    }
    async with aiohttp.ClientSession() as session:
        async with session.post('https://chatgptai.help/wp-json/ai-chatbot/v1/chat',
                                headers=headers, json=json_data, proxy=self.proxies) as response:
            try:
                response.raise_for_status()
                async for line in response.content:
                    line_text = line.decode("utf-8").strip()
                    yield "not_finished", json.loads(line_text).get("reply")
            except Exception as e:
                    raise ConnectionError(f"{__name__}: {e}")

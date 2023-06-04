import sys
import uuid
import json
import httpx
import os

config = json.loads(sys.argv[1])

def session_auth(cookies):
    headers = {
        'authority': 'chat.openai.com',
        'accept': '*/*',
        'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://chat.openai.com/chat',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }

    with httpx.Client() as client:
        headers['x-user-agent'] = 'chrome110'
        response = client.get('https://chat.openai.com/api/auth/session', cookies=cookies, headers=headers)
        return response.json()

env = {key: value.split(',') if value else [] for key, value in os.environ.items()}
try:
    cookies = {
        '__Secure-next-auth.session-token': env['GPT4FREE_CHATGPT_SESSION_TOKEN'][0]
    }
except Exception:
    print('Failed to get "__Secure-next-auth.session-token" in chrome, please make sure you are authenticated on openai.com')
    exit(0)

headers = {
    'authority': 'chat.openai.com',
    'accept': 'text/event-stream',
    'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
    'authorization': 'Bearer ' + session_auth(cookies)['accessToken'],
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://chat.openai.com',
    'pragma': 'no-cache',
    'referer': 'https://chat.openai.com/chat',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'x-user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
}

payload = {
    'action': 'next',
    'history_and_training_disabled': False,
    'messages': [
        {
            'id': str(uuid.uuid4()),
            'author': {
                'role': 'user',
            },
            'content': {
                'content_type': 'text',
                'parts': [
                    config['messages'][-1]['content']
                ]
            }
        }
    ],
    'model': 'text-davinci-002-render-sha',
    'parent_message_id': str(uuid.uuid4()),
    'supports_modapi': True,
    'timezone_offset_min': -60
}

completion = ''

def format(chunk):
    global completion
    
    if b'parts' in chunk:
        json_data = json.loads(chunk.decode('utf-8').split('data: ')[1])
        token = json_data['message']['content']['parts'][0]
        token = token.replace(completion, '')
        completion += token
    
        print(token, flush=True)

with httpx.Client() as client:
    headers['x-user-agent'] = 'chrome110'
    response = client.post('https://chat.openai.com/backend-api/conversation', json=payload, headers=headers, content=client)
    response.read(content_callback=format)
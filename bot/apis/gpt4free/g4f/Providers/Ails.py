import os
import time
import json
import uuid
import hashlib
import requests

from ..typing import sha256, Dict, get_type_hints
from datetime import datetime

url: str = 'https://ai.ls'
model: str = 'gpt-3.5-turbo'


class Utils:
    def hash(json_data: Dict[str, str]) -> sha256:

        secretKey: bytearray = bytearray([79, 86, 98, 105, 91, 84, 80, 78, 123, 83,
                                         35, 41, 99, 123, 51, 54, 37, 57, 63, 103, 59, 117, 115, 108, 41, 67, 76])

        base_string: str = '%s:%s:%s:%s' % (
            json_data['t'],
            json_data['m'],
            'OVbi[TPN{S#)c{36%9?g;usl)CL',
            len(json_data['m'])
        )
        
        return hashlib.sha256(base_string.encode()).hexdigest()

    def format_timestamp(timestamp: int) -> str:

        e = timestamp
        n = e % 10
        r = n + 1 if n % 2 == 0 else n
        return str(e - n + r)


def _create_completion(model: str,messages: list, temperature: float = 0.6, stream: bool = False):
    headers = {
        'authority': 'api.caipacity.com',
        'accept': '*/*',
        'authorization': 'Bearer free',
        'client-id': str(uuid.uuid4()),
        'client-v': '0.1.26',
        'content-type': 'application/json',
        'origin': 'https://ai.ls',
        'referer': 'https://ai.ls/',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    }

    timestamp = Utils.format_timestamp(int(time.time() * 1000))

    sig = {
        'd': datetime.now().strftime('%Y-%m-%d'),
        't': timestamp,
        's': Utils.hash({
            't': timestamp,
            'm': messages[-1]['content']})}

    json_data = json.dumps(separators=(',', ':'), obj={
        'model': 'gpt-3.5-turbo',
        'temperature': temperature,
        'stream': True,
        'messages': messages} | sig)

    response = requests.post('https://api.caipacity.com/v1/chat/completions?full=false',
                             headers=headers, data=json_data, stream=True)

    for token in response.iter_lines():
        yield token.decode()

params = f'g4f.Providers.{os.path.basename(__file__)[:-3]} supports: ' + \
    '(%s)' % ', '.join([f"{name}: {get_type_hints(_create_completion)[name].__name__}" for name in _create_completion.__code__.co_varnames[:_create_completion.__code__.co_argcount]])
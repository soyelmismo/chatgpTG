import requests
import apis.opengpt.chatbase as chatbase
import time
import config

def estadosapi():
    vivas = []
    num_errores = 0
    for recorrido in config.api["available_api"]:
        url = config.api["info"][recorrido]["url"]
        key = config.api["info"][recorrido].get("key", "")
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + key,
        }

        json_data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'user',
                    'content': 'say pong',
                },
            ],
        }

        try:
            if recorrido == "chatbase":
                response = chatbase.GetAnswer(messages="say pong")
            else:
                response = requests.post(f'{url}/chat/completions', headers=headers, json=json_data, timeout=10)
            if isinstance(response, str):
                if recorrido == "chatbase":
                    #if porque los mamaverga filtran la ip en el mensaje
                    if "API rate limit exceeded" in response:
                        print("límite de API en chatbase!")
                    vivas.append(recorrido)
                else:
                    num_errores += 1
            elif response.status_code == 200:
                vivas.append(recorrido)
            else:
                num_errores += 1
        except requests.exceptions.RequestException as e:
            num_errores += 1

        time.sleep(1)

    print(f"Conexión exitosa con {len(vivas)}, malas: {num_errores}")
    return vivas

import requests
import apis.opengpt.chatbase as chatbase
import time
import yaml
from pathlib import Path

config_dir = Path(__file__).parent.parent.resolve() / "config"

# apis
with open(config_dir / "api.yml", 'r') as f:
    api = yaml.safe_load(f)


def estadosapi():
    vivas = []
    num_errores = 0
    for recorrido in api["available_api"]:
        url = api["info"][recorrido]["url"]
        key = api["info"][recorrido].get("key", "")
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
                num_errores += 1
                print(f"{recorrido} API devolvió un error: {response}")
            elif response.status_code == 200:
                vivas.append(recorrido)
                print(f"{recorrido} API vive!")
            else:
                num_errores += 1
                print(f"{recorrido} API no respondió con éxito.")
        except requests.exceptions.RequestException as e:
            num_errores += 1
            print(f"Error en la solicitud de {recorrido} API: {e}")

        time.sleep(1)

    if num_errores == len(api["available_api"]):
        print("No se pudo conectar con ninguna de las APIs.")
    else:
        print(f"Conexión exitosa con {len(vivas)} APIs: {vivas}")
    return vivas

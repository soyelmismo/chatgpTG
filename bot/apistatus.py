import requests
import config

async def estadosapi():
    vivas = []
    malas = []
    test=False
    if test != True:
        print("Se ejecutó chequeo de APIs")
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
                    from apis.opengpt import chatbase
                    response = chatbase.GetAnswer(messages="say pong")
                elif recorrido == "g4f":
                    from apis.gpt4free import g4f
                    provider_name = config.model['info']["g4f-yqcloud"]['name']
                    provider = getattr(g4f.Providers, provider_name)
                    response = g4f.ChatCompletion.create(provider=provider, model='gpt-3.5-turbo', messages = [{"role": "user", "content": f'say pong'}], stream=True)
                    r = ""
                    for chunk in response:
                        r += chunk
                    response = r
                elif recorrido == "you":
                    from apis.gpt4free.foraneo import you
                    response = you.Completion.create(
                        prompt="say pong",
                        detailed=False,
                        include_links=False)
                    response = dict(response)
                else:
                    response = requests.post(f'{url}/chat/completions', headers=headers, json=json_data, timeout=10)
                if isinstance(response, str):
                    if recorrido == "chatbase":
                        #if porque los mamaverga filtran la ip en el mensaje
                        if "API rate limit exceeded" in response:
                            print("Advertencia: Límite temporal de API en chatbase!")
                        vivas.append(recorrido)
                    elif recorrido == "g4f":
                        vivas.append(recorrido)
                    else:
                        malas.append(recorrido)
                elif isinstance(response, dict):
                    if recorrido == "you":
                        if response["text"]:
                            vivas.append(recorrido)
                    else:
                        malas.append(recorrido)
                elif response.status_code == 200:
                    vivas.append(recorrido)
                else:
                    malas.append(recorrido)
            except requests.exceptions.RequestException as e:
                malas.append(recorrido)
    else:
        vivas = config.api["available_api"]
    print(f"Conexión exitosa con {len(vivas)}, malas: {len(malas)}, total: {len(config.api['available_api'])}")
    if vivas:
        print(f"Funcionales: {vivas}")
    if malas:
        print(f"Muertas: {malas}")
    return vivas
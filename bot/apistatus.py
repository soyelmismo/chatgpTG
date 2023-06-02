import asyncio
import requests
import config
vivas = []
malas = []

async def checar_api(nombre_api):
    url = config.api["info"][nombre_api]["url"]
    key = config.api["info"][nombre_api].get("key", "")
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
    if nombre_api == "chatbase":
        from apis.opengpt import chatbase
        respuesta = chatbase.GetAnswer(messages="say pong")
    elif nombre_api == "g4f":
        from apis.gpt4free import g4f
        provider_name = config.model['info']["g4f-yqcloud"]['name']
        provider = getattr(g4f.Providers, provider_name)
        respuesta = g4f.ChatCompletion.create(provider=provider, model='gpt-3.5-turbo', messages=[{"role": "user", "content": 'say pong'}], stream=True)
        chunks = []
        for chunk in respuesta:
            chunks.append(chunk)
        respuesta = ''.join(chunks)
    elif nombre_api == "you":
        from apis.gpt4free.foraneo import you
        respuesta = you.Completion.create(
            prompt="say pong",
            detailed=False,
            include_links=False)
        respuesta = dict(respuesta)
    else:
        respuesta = await asyncio.to_thread(requests.post, f'{url}/chat/completions', headers=headers, json=json_data, timeout=10)
    return respuesta

async def checar_respuesta(nombre_api, respuesta):
    global vivas
    global malas
    try:
        if isinstance(respuesta, str):
            if nombre_api == "chatbase":
                #if porque los mamaverga filtran la ip en el mensaje
                if "API rate limit exceeded" in respuesta:
                    print(f'{config.lang["apicheck"]["warning_chatbase"][config.pred_lang]}')
                vivas.append(nombre_api)
            elif nombre_api == "g4f":
                vivas.append(nombre_api)
            else:
                print(f'{nombre_api} {config.lang["errores"]["error"][config.pred_lang]} check respuesta: string chatbase o g4f?', respuesta)
                malas.append(nombre_api)
        elif isinstance(respuesta, dict):
            if nombre_api == "you":
                if respuesta["text"]:
                    vivas.append(nombre_api)
            else:
                print(f'{nombre_api} {config.lang["errores"]["error"][config.pred_lang]} check respuesta: diccionario you?', respuesta)
                malas.append(nombre_api)
        elif respuesta.status_code == 200:
            vivas.append(nombre_api)
        else:
            print(f'{nombre_api} {config.lang["errores"]["error"][config.pred_lang]} check respuesta: else final', respuesta)
            malas.append(nombre_api)
    except requests.exceptions.RequestException as e:
        print(f'{config.lang["errores"]["error"][config.pred_lang]} check respuesta: exception {e}')
        malas.append(nombre_api)

async def check_api(nombre_api):
    try:
        respuesta = await checar_api(nombre_api)
        await checar_respuesta(nombre_api, respuesta)
    except Exception as e:
        print(f'{config.lang["errores"]["error"][config.pred_lang]} APISTATUS {nombre_api}: {e}')
        malas.append(nombre_api)

async def estadosapi():
    global vivas
    global malas
    test = False
    if test != True:
        print(f'{config.lang["apicheck"]["inicio"][config.pred_lang]}')
        tasks = [check_api(nombre_api) for nombre_api in config.api["available_api"]]
        await asyncio.gather(*tasks)
    else:
        vivas = config.api["available_api"]
    print(f'{config.lang["apicheck"]["connection"][config.pred_lang]}: {len(vivas)}, {config.lang["apicheck"]["bad"][config.pred_lang]}: {len(malas)}, {config.lang["apicheck"]["total"][config.pred_lang]}: {len(config.api["available_api"])}')
    if vivas:
        print(f'{config.lang["apicheck"]["working"][config.pred_lang]}: {vivas}')
    if malas:
        print(f'{config.lang["apicheck"]["dead"][config.pred_lang]}: {malas}')
    return vivas
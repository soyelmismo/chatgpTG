import os
from pathlib import Path
from json import load
from dotenv import load_dotenv
load_dotenv()

# parse environment variables
env = {key: os.getenv(key).split(',') if os.getenv(key) else [] for key in os.environ}
telegram_token = env.get('TELEGRAM_TOKEN', [])[0]
itemspage = int(env.get('MAX_ITEMS_PER_PAGE', [10])[0])
columnpage = int(env.get('MAX_COLUMNS_PER_PAGE', [2])[0])

user_whitelist = env.get('USER_WHITELIST', [])
chat_whitelist = env.get('CHAT_WHITELIST', [])
json_database = bool(env.get('WITHOUT_MONGODB', ['False'])[0].lower() == 'true')
dialog_timeout = int(env.get('DIALOG_TIMEOUT', [7200])[0])
n_images = int(env.get('OUTPUT_IMAGES', [4])[0])
if json_database != True:
    mongus = env.get("MONGODB_HOST", ['mongo'])[0]
    if "mongodb.net" in mongus:
        MONGODB_PROTO = "mongodb+srv"
    else:
        MONGODB_PROTO = "mongodb"

    mongodb_uri = f"{MONGODB_PROTO}://{env.get('MONGODB_USERNAME', ['root'])[0]}:{env.get('MONGODB_PASSWORD', ['MMWjHEHT8zd3FMR5KPd7eu6MKV2ndpUd'])[0]}@{mongus}/?retryWrites=true&w=majority"
disable_apis_checkers = bool(env.get('DISABLE_APIS_CHECK', ['False'])[0].lower() == 'true')
url_ask_before_send = bool(env.get('URL_DIRECT_RESPONSE', ['True'])[0].lower() == 'true')
usar_streaming = bool(env.get('STREAM_ANSWERS', ['True'])[0].lower() == 'true')
usar_funciones = bool(env.get('FEATURE_FUNCTION_CALLS', ['True'])[0].lower() == 'true')
timeout_ask = bool(env.get('TIMEOUT_ASK', ['True'])[0].lower() == 'true')
switch_voice = bool(env.get('FEATURE_TRANSCRIPTION', ['True'])[0].lower() == 'true')
switch_ocr = bool(env.get('FEATURE_IMAGE_READ', ['True'])[0].lower() == 'true')
switch_docs = bool(env.get('FEATURE_DOCUMENT_READ', ['True'])[0].lower() == 'true')
switch_imgs = bool(env.get('FEATURE_IMAGE_GENERATION', ['True'])[0].lower() == 'true')
switch_search = bool(env.get('FEATURE_BROWSING', ['True'])[0].lower() == 'true')
switch_urls = bool(env.get('FEATURE_URL_READ', ['True'])[0].lower() == 'true')
audio_max_size = int(env.get('AUDIO_MAX_MB', [20])[0])
generatedimagexpiration = int(env.get('GENERATED_IMAGE_EXPIRATION_MINUTES', ['5'])[0])
file_max_size = int(env.get('DOC_MAX_MB', [10])[0])
url_max_size = int(env.get('URL_MAX_MB', [5])[0])

max_retries = int(env.get('REQUEST_MAX_RETRIES', [3])[0])

request_timeout = int(env.get('REQUEST_TIMEOUT', [10])[0])
pdf_page_lim = int(env.get('PDF_PAGE_LIMIT', [25])[0])
pred_lang = str(env.get('AUTO_LANG', ['en'])[0])

custom_imaginepy_url = env.get('IMAGINE_URL', [None])[0]

proxy_raw = env.get('API_TUNNEL', [None])[0]
apisproxy = {proxy_raw.split("://")[0] + "://": proxy_raw} if proxy_raw is not None else None

basepath = Path(__file__).resolve().parents[3]
# set config paths
config_dir = basepath / "config"
# load config files

#language
# Obtener la lista de archivos en la carpeta
archivos = os.listdir(basepath / "locales")
# Filtrar los archivos que tienen el formato <lang>.json
archivos_idiomas = [archivo for archivo in archivos if archivo.endswith(".json") and archivo != "props.json"]
# Extraer el código de idioma de cada archivo y generar la lista
available_lang = [archivo.split(".")[1] for archivo in archivos_idiomas]

especificacionlang = "El bot debe responder a todos los mensajes exclusivamente en idioma {language}"
lang = {}

for locale in available_lang:
    with open(basepath / f"locales/lang.{locale}.json", "r", encoding="utf-8") as infile:
        lang[locale] = load(infile)

# apis
with open(config_dir / "api.json", 'r', encoding="utf-8") as f:
    api = load(f)

# chat_modes
with open(config_dir / "chat_mode.json", 'r', encoding="utf-8") as f:
    chat_mode = load(f)

# models
with open(config_dir / "model.json", 'r', encoding="utf-8") as f:
    model = load(f)

#completion_options
with open(config_dir / "openai_completion_options.json", 'r', encoding="utf-8") as f:
    completion_options = load(f)

#props
with open(basepath / "locales/props.json", 'r', encoding="utf-8") as f:
    props = load(f)

# set file pathsfrom
help_group_chat_video_path = basepath / "static" / "help_group_chat.mp4"

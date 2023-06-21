import os
from pathlib import Path
import yaml
from dotenv import load_dotenv
load_dotenv()

# parse environment variables
env = {key: value.split(',') if value else [] for key, value in os.environ.items()}
telegram_token = env.get('TELEGRAM_TOKEN', [])[0]
itemspage = int(env.get('MAX_ITEMS_PER_PAGE', [10])[0])
columnpage = int(env.get('MAX_COLUMNS_PER_PAGE', [2])[0])

user_whitelist = env.get('USER_WHITELIST', [])
chat_whitelist = env.get('CHAT_WHITELIST', [])

dialog_timeout = int(env.get('DIALOG_TIMEOUT', [7200])[0])
n_images = int(env.get('OUTPUT_IMAGES', [4])[0])

mongus = env.get("MONGODB_HOST", ['mongo'])[0]
if "mongodb.net" in mongus:
    MONGODB_PROTO = "mongodb+srv"
else:
    MONGODB_PROTO = "mongodb"

mongodb_uri = f"{MONGODB_PROTO}://{env.get('MONGODB_USERNAME', ['root'])[0]}:{env.get('MONGODB_PASSWORD', ['MMWjHEHT8zd3FMR5KPd7eu6MKV2ndpUd'])[0]}@{mongus}/?retryWrites=true&w=majority"
timeout_ask = bool(env.get('TIMEOUT_ASK', [True])[0])
switch_voice = bool(env.get('FEATURE_TRANSCRIPTION', [True])[0])
switch_ocr = bool(env.get('FEATURE_IMAGE_READ', [True])[0])
switch_docs = bool(env.get('FEATURE_DOCUMENT_READ', [True])[0])
switch_imgs = bool(env.get('FEATURE_IMAGE_GENERATION', [True])[0])
switch_search = bool(env.get('FEATURE_BROWSING', [True])[0])
switch_urls = bool(env.get('FEATURE_URL_READ', [True])[0])
audio_max_size = int(env.get('AUDIO_MAX_MB', [20])[0])
generatedimagexpiration = int(env.get('GENERATED_IMAGE_EXPIRATION_MINUTES', ['5'])[0])
file_max_size = int(env.get('DOC_MAX_MB', [10])[0])
url_max_size = int(env.get('URL_MAX_MB', [5])[0])
max_retries = int(env.get('REQUEST_MAX_RETRIES', [3])[0])
request_timeout = int(env.get('REQUEST_TIMEOUT', [10])[0])
pdf_page_lim = int(env.get('PDF_PAGE_LIMIT', [25])[0])
pred_lang = str(env.get('AUTO_LANG', ['en'])[0])

# set config paths
config_dir = Path(__file__).resolve().parents[3] / "config"
# load config files

#language
with open(config_dir / "lang.yml", 'r') as f:
    lang = yaml.safe_load(f)

# apis
with open(config_dir / "api.yml", 'r') as f:
    api = yaml.safe_load(f)

# chat_modes
with open(config_dir / "chat_mode.yml", 'r') as f:
    chat_mode = yaml.safe_load(f)

# models
with open(config_dir / "model.yml", 'r') as f:
    model = yaml.safe_load(f)

#completion_options
with open(config_dir / "openai_completion_options.yml", 'r') as f:
    completion_options = yaml.safe_load(f)

#props
with open(config_dir / "props.yml", 'r') as f:
    props = yaml.safe_load(f)

# set file pathsfrom
help_group_chat_video_path = Path(__file__).resolve().parents[3] / "static" / "help_group_chat.mp4"

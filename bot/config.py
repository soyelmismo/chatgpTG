import os
from pathlib import Path
import yaml

# parse environment variables
env = {key: value.split(',') if value else [] for key, value in os.environ.items()}
telegram_token = env['TELEGRAM_TOKEN'][0]
apicheck_minutes = int(env['APICHECK_MINUTES'][0])
user_whitelist = env.get('USER_WHITELIST', [])
dialog_timeout = int(env['DIALOG_TIMEOUT'][0])
n_images = int(env['OUTPUT_IMAGES'][0])
mongodb_uri = f"mongodb://{env['MONGODB_USERNAME'][0]}:{env['MONGODB_PASSWORD'][0]}@{env['MONGODB_HOST'][0]}/?retryWrites=true&w=majority"
timeout_ask = os.environ.get('TIMEOUT_ASK')
audio_max_size = int(env['AUDIO_MAX_MB'][0])
file_max_size = int(env['DOC_MAX_MB'][0])
url_max_size = int(env['URL_MAX_MB'][0])
pdf_page_lim = int(env['PDF_PAGE_LIMIT'][0])
pred_lang = str(env['AUTO_LANG'][0])

# set config paths
config_dir = Path(__file__).parent.parent.resolve() / "config"

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

# set file paths
help_group_chat_video_path = Path(__file__).parent.parent.resolve() / "static" / "help_group_chat.mp4"

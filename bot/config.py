import os
from pathlib import Path
import yaml

# parse environment variables
env = {key: value.split(',') if value else [] for key, value in os.environ.items()}
telegram_token = env['TELEGRAM_TOKEN'][0]
sudo_users = env.get('SUDO_USERS', [])
user_whitelist = env.get('USER_WHITELIST', [])
new_dialog_timeout = int(env['new_dialog_timeout'][0])
n_images = int(env['return_n_generated_images'][0])
mongodb_uri = f"mongodb://{env['MONGODB_USERNAME'][0]}:{env['MONGODB_PASSWORD'][0]}@{env['MONGODB_HOST'][0]}/?retryWrites=true&w=majority"

# set config paths
config_dir = Path(__file__).parent.parent.resolve() / "config"
api_path = config_dir / "api.yml"
chat_mode_path = config_dir / "chat_mode.yml"
model_path = config_dir / "model.yml"
completion_options_path = config_dir / "openai_completion_options.yml"

# load config files
with open(api_path, 'r') as f:
    api = yaml.load(f, Loader=yaml.FullLoader)

with open(chat_mode_path, 'r') as f:
    chat_mode = yaml.load(f, Loader=yaml.FullLoader)

with open(model_path, 'r') as f:
    model = yaml.load(f, Loader=yaml.FullLoader)

with open(completion_options_path, 'r') as f:
    completion_options = yaml.load(f, Loader=yaml.FullLoader)

# set file paths
help_group_chat_video_path = Path(__file__).parent.parent.resolve() / "static" / "help_group_chat.mp4"

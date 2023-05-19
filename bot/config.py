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

# load config files
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

# tokens
with open(config_dir / "max_tokens.yml", 'r') as f:
    max_tokens = yaml.safe_load(f)

# set file paths
help_group_chat_video_path = Path(__file__).parent.parent.resolve() / "static" / "help_group_chat.mp4"

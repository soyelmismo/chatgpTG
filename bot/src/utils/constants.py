import logging
logger = logging.getLogger('ChatGPTG')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(name)s | %(levelname)s > %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


constant_db_model = "current_model"
constant_db_chat_mode = "current_chat_mode"
constant_db_image_api = "current_image_api"
constant_db_image_api_styles = "current_image_api_style"
constant_db_imaginepy_styles = "current_imaginepy_style"
constant_db_imaginepy_ratios = "current_imaginepy_ratio"
constant_db_imaginepy_models = "current_imaginepy_model"

constant_db_api = "current_api"
constant_db_lang = "current_lang"
constant_db_tokens = "current_max_tokens"
continue_key = "Renounce€Countless€Unrivaled2€Banter"

from bot.src.apis.imagine import Style
image_api_styles = [style.name for style in Style]

#imaginepy_styles = [style.name for style in Style]
#imaginepy_ratios = [ratio.name for ratio in Ratio]
#imaginepy_models = [model.name for model in Model]
imaginepy_styles = None
imaginepy_ratios = None
imaginepy_models = None
ERRFUNC = "Error retrieving function."
FUNCNOARG = "No se encontraron argumentos de busqueda. por favor pidele al usuario qué quiere buscar."

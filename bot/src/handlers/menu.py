from bot.src.start import Update, CallbackContext
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.src.utils import proxies
from bot.src.utils.proxies import menu_cache, config, db, obtener_contextos as oc, parametros, interaction_cache, msg_no_mod, ParseMode, telegram, errorpredlang
from bot.src.utils import constants

async def get(menu_type, update: Update, context: CallbackContext, chat, page_index):
    try:
        option_name, current_key = None, None
        _, lang = await oc(update)
        menu_type_dict = await get_menu_type_dict(menu_type)
        if menu_type in ["props", "imaginepy", "image_api_styles", "stablehorde"]:
            current_key = None
        else:
            current_key = await get_current_key(menu_type, chat)
        if not current_key:
            option_name = None
        else:
            option_name = await get_option_name(menu_type, menu_type_dict, lang, current_key)
        text = await get_text(update, context, chat, lang, menu_type, menu_type_dict, option_name, current_key)
        item_keys = await get_menu_item_keys(menu_type, chat, lang, update)
        item_keys.remove("imagen") if config.switch_imgs != True and "imagen" in item_keys else None
        keyboard = await get_keyboard(item_keys, page_index, menu_type, menu_type_dict, lang)
        reply_markup = InlineKeyboardMarkup(keyboard)
        return text, reply_markup
    except Exception as e: constants.logger.error(f'{__name__}: {errorpredlang}: <get_menu> <{menu_type}, {option_name}, {current_key}> {e}')

type_dict = {
    "props": config.props,
    "imaginepy": config.props,
    "imaginepy_styles": constants.imaginepy_styles,
    "imaginepy_ratios": constants.imaginepy_ratios,
    "imaginepy_models": constants.imaginepy_models,
}

async def get_menu_type_dict(menu_type: str):
    try:
        if menu_type == "image_api":
            return config.api
        if menu_type == "image_api_styles":
            return constants.image_api_styles
        if menu_type == "stablehorde":
            return config.props
        if menu_type == "stablehorde_models":
            return constants.stablehorde_models
        return type_dict.get(menu_type, getattr(config, menu_type))
    except Exception as e:
        raise ValueError(f'<get_menu_type_dict> {e}')

async def get_current_key(menu_type, chat):
    try:
        constant_name = "constant_db_" + menu_type
        constant_value = constants.__dict__[constant_name]
        cache_variable = getattr(proxies, f"{menu_type}_cache")
        if chat.id in cache_variable: current_key = cache_variable[chat.id][0]
        else: current_key = await db.get_chat_attribute(chat, constant_value)
        cache_variable[chat.id] = (current_key, datetime.now())
        return current_key
    except Exception as e:
        raise ValueError(f'<get_current_key> {e}')


async def get_name_from_info_dict(**kwargs): return kwargs["menu_type_dict"]["info"][kwargs["current_key"]]["name"]

async def get_name_from_info_dict_with_lang(**kwargs): return kwargs["menu_type_dict"]["info"][kwargs["current_key"]]["name"][kwargs["lang"]]

async def get_name_from_image_api_styles(**kwargs): return constants.Style[kwargs["current_key"]].value[1]

async def get_name_from_imaginepy_styles(**kwargs): return constants.imaginepy_styles[constants.imaginepy_styles.index(kwargs["current_key"])]

async def get_name_from_imaginepy_ratios(**kwargs): return constants.imaginepy_ratios[constants.imaginepy_ratios.index(kwargs["current_key"])]

async def get_name_from_imaginepy_models(**kwargs): return constants.imaginepy_models[constants.imaginepy_models.index(kwargs["current_key"])]

async def get_name_from_stablehorde_models(**kwargs): return constants.stablehorde_models.get(int(kwargs["current_key"]))


async def get_name_from_lang(**kwargs): return kwargs["menu_type_dict"][kwargs["lang"]]["info"]["name"]

menu_type_to_function = {
    "props": None,
    "imaginepy": None,
    "stablehorde": None,
    "api": get_name_from_info_dict,
    "model": get_name_from_info_dict,
    "imaginepy_styles": get_name_from_imaginepy_styles,
    "imaginepy_ratios": get_name_from_imaginepy_ratios,
    "imaginepy_models": get_name_from_imaginepy_models,
    "stablehorde_models": get_name_from_stablehorde_models,
    "chat_mode": get_name_from_info_dict_with_lang,
    "lang": get_name_from_lang,
    "image_api": get_name_from_info_dict,
    "image_api_styles": get_name_from_image_api_styles,
}

async def get_option_name(menu_type, menu_type_dict, lang, current_key):
    try:
        if menu_type == "stablehorde_models": return current_key

        kwargs = {
            "menu_type_dict": config.api if menu_type == "image_api" else menu_type_dict,
            "current_key": current_key,
            "lang": lang,
        }
        func = menu_type_to_function.get(menu_type)
        return await func(**kwargs)
    except Exception as e: raise KeyError(f"get_option_name: {e}")

async def get_imaginepy_text(chat, lang):
    try:
        nombremenu = config.api["info"]["imaginepy"]["name"]
        descripcionmenu = config.api["info"]["imaginepy"]["description"][lang]
        estilo = config.lang[lang]["metagen"]["imaginepy_styles"]
        ratio = config.lang[lang]["metagen"]["imaginepy_ratios"]
        model = config.lang[lang]["metagen"]["modelo"]
        styleactual = await db.get_chat_attribute(chat, constants.constant_db_imaginepy_styles)
        ratioactual = await db.get_chat_attribute(chat, constants.constant_db_imaginepy_ratios)
        modelactual = await db.get_chat_attribute(chat, constants.constant_db_imaginepy_models)
        textoprimero = """{nombre}\n{descripcion}\n\n{actual}:\n{estilo}: {styleactual}\n{model}: {modelactual}\n{ratio}: {ratioactual}"""
        return f"{textoprimero.format(nombre=nombremenu, descripcion=descripcionmenu, actual=config.lang[lang]['info']['actual'], estilo=estilo, styleactual=styleactual,ratio=ratio, ratioactual=ratioactual, model=model, modelactual=modelactual)}"
    except Exception as e:
        raise ValueError(f'<get_imaginepy_text> {e}')

async def get_image_api_text(chat, lang, stablehorde=None):
    try:
        retr = [constants.constant_db_image_api, constants.constant_db_image_api_styles, constants.constant_db_stablehorde_models]
        data = await db.get_chat_attributes_dict(chat, retr)
        current_key = data[constants.constant_db_image_api]
        styleactual = constants.Style[data[constants.constant_db_image_api_styles]].value[1]
        api_name = await get_option_name("image_api", None, lang, current_key)
        textoprimero = """{actual}: {api_name} / {styleactual}"""
        if stablehorde:
            textoprimero += f"\n{config.lang[lang]['metagen']['modelo']}: {constants.stablehorde_models.get(int(data[constants.constant_db_stablehorde_models]))}"
        return f"{textoprimero.format(actual=config.lang[lang]['info']['actual'], api_name=api_name, styleactual=styleactual)}"
    except Exception as e:
        raise ValueError(f'<get_image_api_text> {e}')

async def get_current_key_text(menu_type, menu_type_dict, option_name, current_key, lang):
    description = (menu_type_dict[lang]['info']['description'] if menu_type == "lang" else
                    menu_type_dict['info'][current_key]['description'][lang])
    return f"<b>{config.lang[lang]['info']['actual']}</b>: {str(option_name)}\n{description}"
async def get_props_text(update, context):
    from .commands import status
    return await status.handle(update, context, paraprops=True)

async def get_text(update, context, chat, lang, menu_type, menu_type_dict, option_name=None, current_key=None):
    try:
        if menu_type == "image_api_styles":
            texto = await get_image_api_text(chat, lang)
        if menu_type in ["imaginepy", "imaginepy_styles", "imaginepy_ratios", "imaginepy_models"]:
            texto = await get_imaginepy_text(chat, lang)
        if menu_type in ["stablehorde", "stablehorde_models"]:
            texto = await get_image_api_text(chat, lang, stablehorde=True)
        elif current_key:
            texto = await get_current_key_text(menu_type, menu_type_dict, option_name, current_key, lang)
        elif menu_type == "props":
            texto = await get_props_text(update, context)
        return f"{texto}\n\n<b>{config.lang[lang]['info']['seleccion']}</b>"
    except Exception as e: 
        raise KeyError(f"get_text: {e}")


async def get_menu_item_keys(menu_type, chat, lang, update):
    from bot.src.tasks.apis_chat import vivas as apis_vivas
    from bot.src.tasks.apis_image import img_vivas
    menu_items = {
        "api": apis_vivas,
        "chat_mode": config.chat_mode["available_chat_mode"],
        "lang": config.available_lang,
        "props": config.props["available_props"],
        "image_api": img_vivas,
        "image_api_styles": constants.image_api_styles,
        "imaginepy": config.props["imaginepy"]["available_options"],
        "stablehorde": config.props["stablehorde"]["available_options"],
        "imaginepy_styles": constants.imaginepy_styles,
        "imaginepy_ratios": constants.imaginepy_ratios,
        "imaginepy_models": constants.imaginepy_models,
        "stablehorde_models": constants.stablehorde_models,
    }

    try:
        if menu_type == "model":
            _, api_actual, _, _, _, _, _ = await parametros(chat, lang, update)
            return config.api["info"][api_actual]["available_model"]
        return menu_items.get(menu_type)
    except Exception as e:
        raise KeyError(f"<get_menu_item_keys> {e}")

def convert_dict_to_immutable(d):
    if isinstance(d, dict): return frozenset((k, convert_dict_to_immutable(v)) for k, v in d.items())
    elif isinstance(d, list): return tuple(convert_dict_to_immutable(x) for x in d)
    return d

async def get_keyboard(item_keys, page_index, menu_type, menu_type_dict, lang):
    try:
        menu_type_dict_immutable = convert_dict_to_immutable(menu_type_dict)
        cache_key = (tuple(item_keys), page_index, menu_type, menu_type_dict_immutable, lang)

        if cache_key in menu_cache: return menu_cache[cache_key]
        else:
            from itertools import islice
            per_page = config.itemspage
            if menu_type in ["stablehorde_models", "image_api_styles"]: per_page = per_page * 2
            page_keys = list(islice(item_keys, page_index * per_page, (page_index + 1) * per_page))
            import math
            num_rows = math.ceil(len(page_keys) / config.columnpage)
            # Crear lista de tuplas para representar el teclado
            kwargs = {
                "menu_type_dict": config.api if menu_type == "image_api" else menu_type_dict,
                "lang": lang,
            }
            func = await get_item_name(menu_type)
            keyboard_data = await gen_keyboard_data(page_keys, func, menu_type, page_index, **kwargs)
            # Convertir la lista de tuplas en una matriz bidimensional de botones InlineKeyboardButton
            keyboard = await gen_keyboard_buttons(num_rows, keyboard_data)
            keyboard = await get_navigation_buttons(keyboard, item_keys, page_index, menu_type, lang)
            menu_cache[cache_key] = keyboard
            return keyboard
    except Exception as e: raise KeyError(f"get_keyboard: {e}")

async def gen_keyboard_data(page_keys, func, menu_type, page_index, **kwargs):
    keyboard_data = []
    try:
        for index, current_key in enumerate(page_keys):
            kwargs["current_key"] = current_key
            name = await func(**kwargs)
            callback_data = f"set_{menu_type}|{current_key}|{page_index}|{menu_type}"
            keyboard_data.append((index, str(name), callback_data))
        return keyboard_data
    except Exception as e:
        raise ValueError(f'<gen_keyboard_data> {e}')

def create_buttons(row_data):
    for index, name, callback_data in row_data:
        yield InlineKeyboardButton(name, callback_data=callback_data)

async def gen_keyboard_buttons(num_rows, keyboard_data):
    keyboard = []
    for row in range(num_rows):
        row_start = row * config.columnpage
        row_end = (row + 1) * config.columnpage
        row_data = keyboard_data[row_start:row_end]
        buttons = list(create_buttons(row_data))
        keyboard.append(buttons)
    return keyboard


async def get_name_from_lang_info(**kwargs): return kwargs["menu_type_dict"]['info']['name'][kwargs["current_key"]]
async def get_name_of_lang(**kwargs):
    return config.lang[kwargs['current_key']]['info']['name']
async def get_name_from_metagen(**kwargs):
    if kwargs["current_key"] in ["imaginepy_models", "stablehorde_models"]:
        return config.lang[kwargs["lang"]]["metagen"]["modelo"]
    if kwargs["current_key"] in ["image_api_styles"]:
        return config.lang[kwargs["lang"]]["metagen"]["imaginepy_styles"]
    return config.lang[kwargs["lang"]]["metagen"][kwargs["current_key"]]

menu_type_to_function = {
    "api": get_name_from_info_dict,
    "model": get_name_from_info_dict,
    "image_api": get_name_from_info_dict,
    "image_api_styles": get_name_from_image_api_styles,
    "chat_mode": get_name_from_info_dict_with_lang,
    "props": get_name_from_info_dict_with_lang,
    "lang": get_name_of_lang,
    "imaginepy": get_name_from_metagen,
    "stablehorde": get_name_from_metagen,
    "imaginepy_styles": get_name_from_imaginepy_styles,
    "imaginepy_ratios": get_name_from_imaginepy_ratios,
    "imaginepy_models": get_name_from_imaginepy_models,
    "stablehorde_models": get_name_from_stablehorde_models
}
#async def get_item_name(menu_type, menu_type_dict, current_key, lang):
async def get_item_name(menu_type):
    try:
        return menu_type_to_function.get(menu_type)
    except Exception as e: raise KeyError(f"get_item_name: {e}")

async def get_navigation_buttons(keyboard, item_keys, page_index, menu_type, lang):
    try:
        navigation_buttons = []
        # Agregar botones de navegación, si es necesario
        if len(item_keys) > config.itemspage:
            if page_index != 0: navigation_buttons.append(InlineKeyboardButton("«", callback_data=f"set_{menu_type}|paginillas|{page_index - 1}|{menu_type}"))
            if menu_type != "props": navigation_buttons.append(InlineKeyboardButton("↩️", callback_data=f"set_props|paginillas|{page_index}|{menu_type}"))
            if (page_index + 1) * config.itemspage < len(item_keys): navigation_buttons.append(InlineKeyboardButton("»", callback_data=f"set_{menu_type}|paginillas|{page_index + 1}|{menu_type}"))
        else:
            if menu_type != "props": navigation_buttons.append(InlineKeyboardButton("↩️", callback_data=f"set_props|paginillas|{page_index}|{menu_type}"))
            if menu_type == "props": navigation_buttons.append(InlineKeyboardButton(f'{config.lang[lang]["commands"]["reset"]} 🪃', callback_data=f'set_props|reset|0|{menu_type}'))
        if navigation_buttons: keyboard.append(navigation_buttons)
        return keyboard
    except Exception as e: raise KeyError(f"get_navigation_buttons: {e}")

async def handle(update: Update):
    try:
        query = update.callback_query
        await query.answer()
        propsmenu = query.data.split("|")[0]
        seleccion = query.data.split("|")[1]
        page_index = int(query.data.split("|")[2])
        is_from_callback = query.data.split("|")[3]
        if page_index < 0: return
        return query, propsmenu, seleccion, page_index, is_from_callback
    except Exception as e: raise ValueError(f'handle: {e}')

async def refresh(query, update, context, page_index, menu_type, chat=None):
    try:
        argus = ((menu_type, update, context, chat, page_index) if chat else
                (menu_type, update, context, page_index))
        text, reply_markup = await get(*argus)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except telegram.error.BadRequest as e:
        if str(e).startswith(msg_no_mod): None
        else: raise ValueError(f'refresh: {e}')
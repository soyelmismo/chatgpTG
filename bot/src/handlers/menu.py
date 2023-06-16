from bot.src.start import Update, CallbackContext
from datetime import datetime
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
async def get(menu_type, update: Update, context: CallbackContext, chat, page_index):
    from bot.src.utils import proxies
    from bot.src.utils.proxies import config, db, obtener_contextos as oc, logger
    cache_variable = getattr(proxies, f"{menu_type}_cache")
    try:
        _, lang = await oc(update)
        menu_type_dict = getattr(config, menu_type)
        current_key = (cache_variable[chat.id][0] if chat.id in cache_variable else
                        await db.get_chat_attribute(chat, f"current_{menu_type}"))
        cache_variable[chat.id] = (current_key, datetime.now())
        item_keys = await get_menu_item_keys(menu_type, menu_type_dict, chat, lang, update)
        item_keys.remove("imagen") if config.switch_imgs != "True" and "imagen" in item_keys else None
        option_name = await get_option_name(current_key, menu_type, menu_type_dict, lang)
        text = await get_text(lang, option_name, menu_type, menu_type_dict, current_key)
        keyboard = await get_keyboard(item_keys, page_index, menu_type, menu_type_dict, lang)
        reply_markup = InlineKeyboardMarkup(keyboard)
        return text, reply_markup
    except Exception as e:
        logger.error(f'<get_menu> {config.lang["errores"]["error"][lang]}: {e}')
async def get_menu_item_keys(menu_type, menu_type_dict, chat, lang, update):
    from bot.src.utils.proxies import (apis_vivas,parametros,config)
    if menu_type != "model" and menu_type != "api":
        item_keys = menu_type_dict[f"available_{menu_type}"]
    elif menu_type == "api":
        item_keys = apis_vivas
    else:
        _, api_actual, _ = await parametros(chat, lang, update)
        item_keys = config.api["info"][api_actual]["available_model"]
    return item_keys

def convert_dict_to_immutable(d):
    return (frozenset((k, convert_dict_to_immutable(v)) for k, v in d.items()) if isinstance(d, dict) else
            tuple(convert_dict_to_immutable(x) for x in d) if isinstance(d, list) else d
            )

async def get_keyboard(item_keys, page_index, menu_type, menu_type_dict, lang):
    from bot.src.utils.proxies import (menu_cache,config)
    
    menu_type_dict_immutable = convert_dict_to_immutable(menu_type_dict)
    cache_key = (tuple(item_keys), page_index, menu_type, menu_type_dict_immutable, lang)
    
    if cache_key in menu_cache:
        return menu_cache[cache_key]
    else:
        per_page = config.itemspage
        page_keys = item_keys[page_index * config.itemspage:(page_index + 1) * per_page]
        import math
        num_rows = math.ceil(len(page_keys) / config.columnpage)
    
        # Crear lista de tuplas para representar el teclado
        keyboard_data = []
        for index, current_key in enumerate(page_keys):
            name = await get_item_name(menu_type, menu_type_dict, current_key, lang)
            callback_data = f"set_{menu_type}|{current_key}|{page_index}"
            keyboard_data.append((index, name, callback_data))
    
        # Convertir la lista de tuplas en una matriz bidimensional de botones InlineKeyboardButton
        keyboard = []
        for row in range(num_rows):
            buttons = [InlineKeyboardButton(name, callback_data=callback_data)
                       for index, name, callback_data in keyboard_data[row * config.columnpage:(row + 1) * config.columnpage]]
            keyboard.append(buttons)
    
        # Agregar botones de navegación, si es necesario
        if len(item_keys) > config.itemspage:
            is_first_page = (page_index == 0)
            is_last_page = ((page_index + 1) * config.itemspage >= len(item_keys))
            navigation_buttons = []
            if not is_first_page:
                navigation_buttons.append(InlineKeyboardButton("«", callback_data=f"set_{menu_type}|paginillas|{page_index - 1}"))
            if not is_last_page:
                navigation_buttons.append(InlineKeyboardButton("»", callback_data=f"set_{menu_type}|paginillas|{page_index + 1}"))
            keyboard.append(navigation_buttons)
        
        menu_cache[cache_key] = keyboard
        return keyboard
        
async def get_item_name(menu_type, menu_type_dict, current_key, lang):
    name = (menu_type_dict["info"][current_key]["name"] if menu_type != "lang" and menu_type != "chat_mode" else
            menu_type_dict["info"][current_key]["name"][lang] if menu_type == "chat_mode" else
            menu_type_dict['info']['name'][current_key])
    return name
async def get_text(lang, option_name, menu_type, menu_type_dict, current_key):
    from bot.src.utils.proxies import (config)
    description = (menu_type_dict['info']['description'][lang] if menu_type == "lang" else
                    menu_type_dict['info'][current_key]['description'][lang])
    return f"<b>{config.lang['info']['actual'][lang]}</b>\n\n{str(option_name)}. {description}\n\n<b>{config.lang['info']['seleccion'][lang]}</b>:"
async def get_option_name(current_key, menu_type, menu_type_dict, lang):
    option_name = (menu_type_dict["info"][current_key]["name"] if menu_type != "chat_mode" and menu_type != "lang" else
                    menu_type_dict["info"][current_key]["name"][lang] if menu_type == "chat_mode" else
                    menu_type_dict["info"]["name"][lang])
    return option_name

async def handle(update: Update):
    query = update.callback_query
    await query.answer()
    seleccion = query.data.split("|")[1]
    page_index = int(query.data.split("|")[2])
    if page_index < 0: return
    return query, page_index, seleccion

async def refresh(query, update, context, page_index, menu_type, chat=None):
    from bot.src.utils.proxies import (db,interaction_cache,msg_no_mod,ParseMode,telegram)
    argus = ((menu_type, update, context, chat, page_index) if chat else
                (menu_type, update, context, page_index))
    text, reply_markup = await get(*argus)
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        interaction_cache[chat.id] = ("visto", datetime.now())
        await db.set_chat_attribute(chat, "last_interaction", datetime.now())
    except telegram.error.BadRequest as e:
        if str(e).startswith(msg_no_mod): pass
            # Ignorar esta excepción específica y continuar la ejecución normalmente  
        else:
            # En caso de otras excepciones BadRequest, manejarlas adecuadamente o agregar acciones adicionales si es necesario
            raise

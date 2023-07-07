import json
from typing import Optional, Any
from uuid import uuid4
from . import config
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorClient
from .constants import (constant_db_model, constant_db_chat_mode, constant_db_api,
                        constant_db_lang, constant_db_tokens, constant_db_image_api,
                        imaginepy_ratios, imaginepy_styles, imaginepy_models, constant_db_imaginepy_styles,
                        constant_db_imaginepy_ratios, constant_db_imaginepy_models)
from pathlib import Path

class Database:
    def __init__(self):
        self.use_json = config.json_database
        self.client = None
        self.db = None
        self.chats = None
        self.dialogs = None
        self.data = None

        if self.use_json:
            self.data_files = {
                "chats": Path("/database/chats.json"),
                "dialogs": Path("/database/dialogs.json")
            }
            self.load_data_from_json()
        else:
            self.client = AsyncIOMotorClient(config.mongodb_uri)
            self.db = self.client["chatgpt"]
            self.chats = self.db["chats"]
            self.dialogs = self.db["dialogs"]

    def load_data_from_json(self):
        self.data = {}
        for key, file_path in self.data_files.items():
            if file_path.exists():
                with file_path.open(encoding="utf-8") as file:
                    self.data[key] = json.load(file)
            else:
                self.data[key] = {}
                self.save_data_to_json(key)  # Guardar datos en el archivo JSON vacío

    def save_data_to_json(self, key: str):
        data = self.convert_datetime(self.data[key])
        with self.data_files[key].open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            
    def convert_datetime(self, data):
        if isinstance(data, dict):
            return {key: self.convert_datetime(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.convert_datetime(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data
      
    async def chat_exists(self, chat, raise_exception: bool = False):
        if self.use_json:
            if self.data["chats"].get(str(chat.id)):
                return True
        else:
            if await self.chats.count_documents({"_id": str(chat.id)}) > 0:
                return True
    
        if raise_exception:
            raise ValueError(f"Chat {str(chat.id)} no existe")
        return False
            

    async def add_chat(self, chat, lang: str):
        if not await self.chat_exists(chat):
            if self.use_json:
                self.data["chats"][str(chat.id)] = {
                    "last_interaction": datetime.now().isoformat(),
                    "current_dialog_id": None,
                    constant_db_lang: lang,
                    constant_db_chat_mode: config.chat_mode["available_chat_mode"][1],
                    constant_db_model: config.model["available_model"][0],
                    constant_db_api: config.api["available_api"][0],
                    constant_db_image_api: config.api["available_image_api"][0],
                    constant_db_imaginepy_styles: imaginepy_styles[0],
                    constant_db_imaginepy_ratios: imaginepy_ratios[0],
                    constant_db_imaginepy_models: imaginepy_models[0],
                }
                self.save_data_to_json("chats")
            else:
                chat_dict = {
                    "_id": str(chat.id),
                    "last_interaction": datetime.now(),
                    "current_dialog_id": None,
                    constant_db_lang: lang,
                    constant_db_chat_mode: config.chat_mode["available_chat_mode"][1],
                    constant_db_model: config.api["info"][config.api["available_api"][0]]["available_model"][0],
                    constant_db_api: config.api["available_api"][0],
                    constant_db_image_api: config.api["available_image_api"][0],
                    constant_db_imaginepy_styles: imaginepy_styles[0],
                    constant_db_imaginepy_ratios: imaginepy_ratios[0],
                    constant_db_imaginepy_models: imaginepy_models[0],
                }
                try:
                    await self.chats.insert_one(chat_dict)
                except DuplicateKeyError:
                    pass

    async def new_dialog(self, chat):
        await self.chat_exists(chat, raise_exception=True)
        dialog_id = str(uuid4())
        if self.use_json:
            self.data["dialogs"][dialog_id] = {
                "chat_id": str(chat.id),
                constant_db_tokens: 0,
                "messages": [],
            }
            self.data["chats"][str(chat.id)]["current_dialog_id"] = dialog_id
            self.save_data_to_json("dialogs")
            self.save_data_to_json("chats")
        else:
            dialog_dict = {
                "_id": dialog_id,
                "chat_id": str(chat.id),
                constant_db_tokens: 0,
                "messages": [],
            }
            # add new dialog
            await self.dialogs.insert_one(dialog_dict)

            # update chat's current dialog
            await self.chats.update_one(
                {"_id": str(chat.id)},
                {"$set": {"current_dialog_id": dialog_id}}
            )

        return dialog_id

    async def get_chat_attribute(self, chat, key: str):
        await self.chat_exists(chat, raise_exception=True)
        if self.use_json:
            chat_dict = self.data["chats"][str(chat.id)]
        else:
            chat_dict = await self.chats.find_one({"_id": str(chat.id)})
            
        return chat_dict.get(key, None)
        
    async def reset_chat_attribute(self, chat):
        await self.chat_exists(chat, raise_exception=True)
        initial_chat_mode = config.chat_mode["available_chat_mode"][0]
        initial_api = config.api["available_api"][0]
        initial_model = config.api["info"][initial_api]["available_model"][0]
        initial_image = config.api["available_image_api"][0]
        initial_imaginepy_style = imaginepy_styles[0]
        initial_imaginepy_ratio = imaginepy_ratios[0]
        initial_imaginepy_model = imaginepy_models[0]
        if self.use_json: 
            self.data["chats"][str(chat.id)][constant_db_chat_mode] = initial_chat_mode
            self.data["chats"][str(chat.id)][constant_db_model] = initial_model
            self.data["chats"][str(chat.id)][constant_db_api] = initial_api
            self.data["chats"][str(chat.id)][constant_db_image_api] = initial_image
            self.data["chats"][str(chat.id)][constant_db_imaginepy_styles] = initial_imaginepy_style
            self.data["chats"][str(chat.id)][constant_db_imaginepy_ratios] = initial_imaginepy_ratio
            self.data["chats"][str(chat.id)][constant_db_imaginepy_models] = initial_imaginepy_model
            self.save_data_to_json("chats")  # Guardar datos en el archivo JSON
        else:
            # Actualizar los valores en la base de datos
            await self.set_chat_attribute(chat, constant_db_chat_mode, initial_chat_mode)
            await self.set_chat_attribute(chat, constant_db_model, initial_model)
            await self.set_chat_attribute(chat, constant_db_api, initial_api)
            await self.set_chat_attribute(chat, constant_db_image_api, initial_image)
            await self.set_chat_attribute(chat, constant_db_imaginepy_styles, initial_imaginepy_style)
            await self.set_chat_attribute(chat, constant_db_imaginepy_ratios, initial_imaginepy_ratio)
            await self.set_chat_attribute(chat, constant_db_imaginepy_models, initial_imaginepy_model)
            
    async def set_chat_attribute(self, chat, key: str, value: Any):
        await self.chat_exists(chat, raise_exception=True)
        if self.use_json:
            self.data["chats"][str(chat.id)][key] = value
            self.save_data_to_json("chats")
        else:
            await self.chats.update_one({"_id": str(chat.id)}, {"$set": {key: value}})

    async def set_dialog_attribute(self, chat, key: str, value: Any):
        dialog_id = await self.get_chat_attribute(chat, "current_dialog_id")
        if self.use_json:
            if dialog_id and dialog_id in self.data["dialogs"]:
                self.data["dialogs"][dialog_id][key] = value
                self.save_data_to_json("dialogs")
        else:
            await self.dialogs.update_one(
                {"_id": dialog_id},
                {"$set": {key: value}}
            )

    async def get_dialog_attribute(self, chat, key: str):
        dialog_id = await self.get_chat_attribute(chat, "current_dialog_id")
        if self.use_json:
            if dialog_id and dialog_id in self.data["dialogs"]:
                dialog_dict = self.data["dialogs"][dialog_id]
        else:
            dialog_dict = await self.dialogs.find_one({"_id": dialog_id})

        return dialog_dict.get(key, None)

    async def get_dialog_messages(self, chat, dialog_id: Optional[str] = None):
        await self.chat_exists(chat, raise_exception=True)
        if dialog_id is None:
            dialog_id = await self.get_chat_attribute(chat, "current_dialog_id")
        if self.use_json:
            if dialog_id and dialog_id in self.data["dialogs"]:
                return self.data["dialogs"][dialog_id]["messages"]
            return []
        else:
            dialog_dict = await self.dialogs.find_one({"_id": dialog_id, "chat_id": str(chat.id)})
            return dialog_dict["messages"]

    async def set_dialog_messages(self, chat, dialog_messages: list, dialog_id: Optional[str] = None):
        await self.chat_exists(chat, raise_exception=True)
        if dialog_id is None:
            dialog_id = await self.get_chat_attribute(chat, "current_dialog_id")
        if self.use_json:
            if dialog_id:
                if dialog_id in self.data["dialogs"]:
                    self.data["dialogs"][dialog_id]["messages"] = dialog_messages
                    self.save_data_to_json("dialogs")
        else:
            await self.dialogs.update_one(
                {"_id": dialog_id, "chat_id": str(chat.id)},
                {"$set": {"messages": dialog_messages}}
            )

    async def delete_all_dialogs_except_current(self, chat):
        if self.use_json:
            if str(chat.id) in self.data["chats"]:
                current_dialog_id = self.data["chats"][str(chat.id)].get("current_dialog_id")
                chat_id = str(chat.id)
                self.data["dialogs"] = {
                    dialog_id: dialog_data
                    for dialog_id, dialog_data in self.data["dialogs"].items()
                    if not (dialog_data["chat_id"] == chat_id and dialog_id != current_dialog_id)
                }
                self.save_data_to_json("dialogs")
        else:
            chat = await self.chats.find_one({"_id": str(chat.id)})
            if not chat:
                raise ValueError(f"Chat with ID {str(chat.id)} does not exist")
            current_dialog_id = chat["current_dialog_id"]
            await self.dialogs.delete_many({"chat_id": chat["_id"], "_id": {"$ne": current_dialog_id}})
            
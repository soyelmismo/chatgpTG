from typing import Optional, Any
import uuid
from . import config
from datetime import datetime
import motor.motor_asyncio
from .constants import constant_db_model, constant_db_chat_mode, constant_db_api, constant_db_lang, constant_db_tokens
class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(config.mongodb_uri)
        self.db = self.client["chatgpt"]
        self.chats = self.db["chats"]
        self.dialogs = self.db["dialogs"]

    async def chat_exists(self, chat, raise_exception: bool = False):
        if await self.chats.count_documents({"_id": chat.id}) > 0:
            return True
        else:
            if raise_exception:
                raise ValueError(f"Chat {chat.id} no existe")
            else:
                return False

    async def add_chat(self, chat, lang: str):
        chat_dict = {
            "_id": chat.id,
            "last_interaction": datetime.now(),
            "current_dialog_id": None,
            f'{constant_db_lang}': lang,
            f'{constant_db_chat_mode}': config.chat_mode["available_chat_mode"][1],
            f'{constant_db_model}': config.model["available_model"][0],
            f'{constant_db_api}': config.api["available_api"][0],
        }
        if not await self.chat_exists(chat):
            await self.chats.insert_one(chat_dict)

    async def new_dialog(self, chat):
        await self.chat_exists(chat, raise_exception=True)
        dialog_id = str(uuid.uuid4())
        dialog_dict = {
            "_id": dialog_id,
            "chat_id": chat.id,
            f'{constant_db_tokens}': 0,
            "messages": [],
        }

        # add new dialog
        await self.dialogs.insert_one(dialog_dict)

        # update chat's current dialog
        await self.chats.update_one(
            {"_id": chat.id},
            {"$set": {"current_dialog_id": dialog_id}}
        )

        return dialog_id

    async def get_chat_attribute(self, chat, key: str):
        await self.chat_exists(chat, raise_exception=True)
        chat_dict = await self.chats.find_one({"_id": chat.id})

        if key not in chat_dict:
            return None

        return chat_dict[key]
    
    async def reset_chat_attribute(self, chat):
        await self.chat_exists(chat, raise_exception=True)

        # Obtener los valores iniciales para cada atributo
        initial_chat_mode = config.chat_mode["available_chat_mode"][0]
        initial_model = config.model["available_model"][0]
        initial_api = config.api["available_api"][0]

        # Actualizar los valores en la base de datos
        await self.set_chat_attribute(chat, f'{constant_db_chat_mode}', initial_chat_mode)
        await self.set_chat_attribute(chat, f'{constant_db_model}', initial_model)
        await self.set_chat_attribute(chat, f'{constant_db_api}', initial_api)
        from .proxies import chat_mode_cache, model_cache, api_cache
        chat_mode_cache[chat.id] = (initial_chat_mode, datetime.now())
        model_cache[chat.id] = (initial_model, datetime.now())
        api_cache[chat.id] = (initial_api, datetime.now())

    async def set_chat_attribute(self, chat, key: str, value: Any):
        await self.chat_exists(chat, raise_exception=True)
        await self.chats.update_one({"_id": chat.id}, {"$set": {key: value}})

    async def set_dialog_attribute(self, chat, key: str, value: Any):
        dialog_id = await self.get_chat_attribute(chat, "current_dialog_id")

        await self.dialogs.update_one(
            {"_id": dialog_id},
            {"$set": {key: value}}
        )
    async def get_dialog_attribute(self, chat, key: str):
        dialog_id = await self.get_chat_attribute(chat, "current_dialog_id")
        dialog_dict = await self.dialogs.find_one({"_id": dialog_id})
        if key not in dialog_dict:
            return None
        return dialog_dict[key]

    async def get_dialog_messages(self, chat, dialog_id: Optional[str] = None):
        await self.chat_exists(chat, raise_exception=True)

        if dialog_id is None:
            dialog_id = await self.get_chat_attribute(chat, "current_dialog_id")

        dialog_dict = await self.dialogs.find_one({"_id": dialog_id, "chat_id": chat.id})
        return dialog_dict["messages"]

    async def set_dialog_messages(self, chat, dialog_messages: list, dialog_id: Optional[str] = None):
        await self.chat_exists(chat, raise_exception=True)

        if dialog_id is None:
            dialog_id = await self.get_chat_attribute(chat, "current_dialog_id")

        await self.dialogs.update_one(
            {"_id": dialog_id, "chat_id": chat.id},
            {"$set": {"messages": dialog_messages}}
        )

    async def delete_all_dialogs_except_current(self, chat):
        chat = await self.chats.find_one({"_id": chat.id})
        if not chat:
            raise ValueError(f"Chat with ID {chat.id} does not exist")
        current_dialog_id = chat["current_dialog_id"]
        await self.dialogs.delete_many({"chat_id": chat["_id"], "_id": {"$ne": current_dialog_id}})
from typing import Optional, Any
import pymongo
import uuid
from datetime import datetime
import config

class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(config.mongodb_uri)
        self.db = self.client["chatgpt"]
        self.chats = self.db["chats"]
        self.dialogs = self.db["dialogs"]

    def chat_exists(self, chat_id: int, raise_exception: bool = False):
        if self.chats.count_documents({"_id": chat_id}) > 0:
            return True
        else:
            if raise_exception:
                raise ValueError(f"Usuario {chat_id} no existe")
            else:
                return False

    def add_chat(self, chat_id: int):
        chat_dict = {
            "_id": chat_id,
            "last_interaction": datetime.now(),
            "first_seen": datetime.now(),

            "current_dialog_id": None,
            "current_chat_mode": config.chat_mode["available_chat_mode"][1],
            "current_model": config.model["available_model"][0],
            "current_api": config.api["available_api"][0],

        }
        if not self.chat_exists(chat_id):
            self.chats.insert_one(chat_dict)

    def new_dialog(self, chat_id: int):
        self.chat_exists(chat_id, raise_exception=True)

        dialog_id = str(uuid.uuid4())
        dialog_dict = {
            "_id": dialog_id,
            "chat_id": chat_id,
            "chat_mode": self.get_chat_attribute(chat_id, "current_chat_mode"),
            "start_time": datetime.now(),
            "model": self.get_chat_attribute(chat_id, "current_model"),
            "api": self.get_chat_attribute(chat_id, "current_api"),
            "messages": [],
        }

        # add new dialog
        self.dialogs.insert_one(dialog_dict)

        # update chat's current dialog
        self.chats.update_one(
            {"_id": chat_id},
            {"$set": {"current_dialog_id": dialog_id}}
        )

        return dialog_id

    def get_chat_attribute(self, chat_id: int, key: str):
        self.chat_exists(chat_id, raise_exception=True)
        chat_dict = self.chats.find_one({"_id": chat_id})

        if key not in chat_dict:
            return None

        return chat_dict[key]
    
    def reset_chat_attribute(self, chat_id: int):
        self.chat_exists(chat_id, raise_exception=True)

        # Obtener los valores iniciales para cada atributo
        initial_chat_mode = config.chat_mode["available_chat_mode"][0]
        initial_model = config.model["available_model"][0]
        initial_api = config.api["available_api"][0]

        # Actualizar los valores en la base de datos
        self.set_chat_attribute(chat_id, 'current_chat_mode', initial_chat_mode)
        self.set_chat_attribute(chat_id, 'current_model', initial_model)
        self.set_chat_attribute(chat_id, 'current_api', initial_api)
        
    def set_chat_attribute(self, chat_id: int, key: str, value: Any):
        self.chat_exists(chat_id, raise_exception=True)
        self.chats.update_one({"_id": chat_id}, {"$set": {key: value}})

    def get_dialog_messages(self, chat_id: int, dialog_id: Optional[str] = None):
        self.chat_exists(chat_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_chat_attribute(chat_id, "current_dialog_id")

        dialog_dict = self.dialogs.find_one({"_id": dialog_id, "chat_id": chat_id})
        return dialog_dict["messages"]

    def set_dialog_messages(self, chat_id: int, dialog_messages: list, dialog_id: Optional[str] = None):
        self.chat_exists(chat_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_chat_attribute(chat_id, "current_dialog_id")

        self.dialogs.update_one(
            {"_id": dialog_id, "chat_id": chat_id},
            {"$set": {"messages": dialog_messages}}
        )

    def delete_all_dialogs_except_current(self, chat_id: int):
        chat = self.chats.find_one({"_id": chat_id})
        if not chat:
            raise ValueError(f"Chat with ID {chat_id} does not exist")

        current_dialog_id = chat["current_dialog_id"]
        self.dialogs.delete_many({"chat_id": chat_id, "_id": {"$ne": current_dialog_id}})
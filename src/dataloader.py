import json
import os
import sys
import threading

from config import Config
from item.data.item_type import ItemType
from logger import Logger

dataloader_lock = threading.Lock()


class Dataloader:
    error_map = dict()
    affix_dict = dict()
    affix_sigil_dict = dict()
    aspect_dict = dict()
    aspect_num_idx = dict()
    aspect_unique_dict = dict()
    aspect_unique_num_idx = dict()
    tooltips = dict()

    _instance = None
    data_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Dataloader, cls).__new__(cls)
            with dataloader_lock:
                if not cls._instance.data_loaded:
                    cls._instance.data_loaded = True
                    cls._instance.load_data()
        return cls._instance

    def load_data(self):
        if "language" not in Config().general:
            Logger.error("Could not load assets. Config not initalized!")
            sys.exit(-1)

        language = Config().general['language']
        lang_path = f"assets/lang/{language}"

        def load_json_file(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        self.affix_dict: dict = self.load_json_file(os.path.join(lang_path, "affixes.json"))

        affix_sigil_dict_all = self.load_json_file(os.path.join(lang_path, "sigils.json"))
        self.affix_sigil_dict = {
            **affix_sigil_dict_all["dungeons"],
            **affix_sigil_dict_all["minor"],
            **affix_sigil_dict_all["major"],
            **affix_sigil_dict_all["positive"],
        }

        data = self.load_json_file(os.path.join(lang_path, "corrections.json"))
        self.error_map = data["error_map"]
        self.filter_after_keyword = data["filter_after_keyword"]
        self.filter_words = data["filter_words"]

        data = self.load_json_file(os.path.join(lang_path, "aspects.json"))
        for key, d in data.items():
            self.aspect_dict[key] = d["desc"][:MAX_DESC_LENGTH]
            self.aspect_num_idx[key] = d["num_idx"]

        data = self.load_json_file(os.path.join(lang_path, "uniques.json"))
        for key, d in data.items():
            self.aspect_unique_dict[key] = d["desc"][:MAX_DESC_LENGTH]
            self.aspect_unique_num_idx[key] = d["num_idx"]

        data = self.load_json_file(os.path.join(lang_path, "item_types.json"))
        for item, value in data.items():
            if item in ItemType.__members__:
                enum_member = ItemType[item]
                enum_member._value_ = value
            else:
                Logger.warning(f"{item} type not in item_type.py")

        self.tooltips = self.load_json_file(os.path.join(lang_path, "tooltips.json"))

    def load_json_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)


MAX_DESC_LENGTH = 45

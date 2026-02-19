import yaml, os
from ruamel.yaml import YAML
from uuid import uuid4
from asyncio import Semaphore
import os

class ConfigurationYaml:
    def __init__(
        self,
        mapping: int = 2,
        sequence: int = 4,
        offset: int = 2,
        default_fs: bool = False,
        enc: str = "utf-8",
    ) -> None:
        yaml2 = YAML()
        yaml2.indent(mapping=mapping, sequence=sequence, offset=offset)
        yaml2.default_flow_style = default_fs
        yaml2.encoding = enc
        self.yaml_conf = yaml2


class UGUtils:
    def __init__(self, yaml_file: str) -> None:
        self.path = yaml_file
        self.data = self.get_yaml()

    def get_yaml(self) -> dict:
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as file:
                file.write("")

        with open(self.path, encoding="utf-8") as file:
            data = yaml.safe_load(file)

            if not data:
                return {}
            return data


    def update_yaml(self, data: dict):
        yaml_config = ConfigurationYaml().yaml_conf
        with open(self.path, "w", encoding="utf-8") as file:
            data = yaml_config.dump(data, file)

        if data:
            return data
        return {}


class Chanel:
    def __init__(self, data : dict):
        self.id : str = data.get('id')
        self.username : str = data.get('username')
        self.name = data.get('name')
        self.url = data.get('url')


class DatabseConfig:
    def __init__(self, data : dict) -> None:
        self.user = data.get('user', 'postgres')
        self.password = data.get("password", '1234')
        self.database = data.get("database", 'database')
        self.port = data.get('port', 5432)
        self.host = data.get('host', 'localhost')


class SavedMessage:        
    def __init__(self, data : dict):
        self.message_id : int = data.get('message_id')
        self.caption : str = data.get('caption')
        self.text: str = data.get('text')
        # stored as 'content_type' by _extract_message_data; fall back to 'type' for old data
        self.content_type: str = data.get('content_type') or data.get('type')
        self.file_id: str = data.get('file_id')
        self.parse_mode: str = data.get('parse_mode')

    @property
    def exists(self) -> bool:
        """True if a message has actually been saved (content_type was set)."""
        return bool(self.content_type)

    @property
    def data(self) -> dict:
        return {
            'content_type' : self.content_type,
            'message_id' : self.message_id,
            'caption' : self.caption,
            'text' : self.text,
            'file_id' : self.file_id,
            'parse_mode' : self.parse_mode
        }


class ParamsDB:
    def __init__(self, config_path : str) -> None:
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        self.yaml = UGUtils(config_path)
        self.params_data = self.yaml.get_yaml()
    
        self.config = DatabseConfig(self.params_data.get('database', {}))
        self.TOKEN = self.params_data.get('token')
        self.DATA_CHANEL_ID : int = self.params_data.get('data_chanel_id')
        self.dev_id : int = self.params_data.get('dev_id')
        self.chanels : list[dict] = self.params_data.get('chanels', [])
        self.welcome_message : str = self.params_data.get('welcome_media')
        self.BONUS_CHNNAEL_ID = self.params_data.get('bonus_chanel_id', -1002598868618)
        self.BONUS_CHANEL_URL = self.params_data.get('bonus_chanel_url', 'https://t.me/+JnmQJIWlgTw2YzAy')
        self.BONUS_POINT = self.params_data.get('bonus_point', 1)
        self.GIFT_POINT = self.params_data.get('gift_point', 2)

        self.SUBSCRIBE_MESSAGE = self.params_data.get('subscribe_message', "Ko'nkursda qatnaish uchun pastdagi tugmani bosing 👇👇👇")
        self.SHARE_MESSAGE = SavedMessage(self.params_data.get('share_message', {}))
        self.ABOUT_LESSONS_MESSAGE = SavedMessage(self.params_data.get('about_lessons_message', {}))        
        self.START_MESSAGE = SavedMessage(self.params_data.get('start_message', {}))
        

        self.paramas_sem = Semaphore()

    @property
    def chanels_len(self) -> int:
        return len(self.chanels)
    
    async def update_params(self):
        async with self.paramas_sem:
            self.yaml.update_yaml(self.params_data)

    async def add_channel(self, data: dict):
        async with self.paramas_sem:
            self.chanels.append(data)
            self.params_data['chanels'] = self.chanels
            self.yaml.update_yaml(self.params_data)

    async def remove_channel(self, channel_id: int):
        async with self.paramas_sem:
            self.chanels = [c for c in self.chanels if c.get('id') != channel_id]
            self.params_data['chanels'] = self.chanels
            self.yaml.update_yaml(self.params_data)

    async def update_save_message(self, key: str, save_message: SavedMessage):
        async with self.paramas_sem:
            self.params_data[key] = save_message.data
            self.yaml.update_yaml(self.params_data)
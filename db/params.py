import yaml, os
from ruamel.yaml import YAML
from uuid import uuid4
from asyncio import Semaphore

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


class ParamsDB:
    def __init__(self, config_path : str) -> None:
        self.yaml = UGUtils(config_path)
        self.params_data = self.yaml.get_yaml()
    
        self.config = DatabseConfig(self.params_data.get('database', {}))
        self.TOKEN = self.params_data.get('token')
        self.DATA_CHANEL_ID : int = self.params_data.get('data_chanel_id')
        self.dev_id : int = self.params_data.get('dev_id')
        self.chanels : list[dict] = self.params_data.get('chanels', [])
        self.need_invate : int = self.params_data.get('need_invate', 1)
        self.need_subscribe_message : int = self.params_data.get('need_subscribe_message', 4)
        self.welcome_message : str = self.params_data.get('welcome_media')
        self.BONUS_CHNNAEL_ID = self.params_data.get('bonus_chanel_id', -1002598868618)
        self.BONUS_CHANEL_URL = self.params_data.get('bonus_chanel_url', 'https://t.me/+JnmQJIWlgTw2YzAy')
        self.BONUS_POINT = self.params_data.get('bonus_point', 1)
        self.GIFT_POINT = self.params_data.get('gift_point', 2)
        
        self.paramas_sem = Semaphore()

    @property
    def chanels_len(self) -> int:
        return len(self.chanels)
    
    async def update_params(self):
        async with self.paramas_sem:
            self.yaml.update_yaml(self.params_data)


# get_settings.py
from utils import Yaml_tool


class Config(object):
    ENV=None
    FILE=None
    def __init__(self):
        self.yaml_tool = Yaml_tool()
        # print(f'env: {Config.ENV}')

    def get_config(self):
        print(f'env: {Config.FILE}')
        data = self.yaml_tool.read_yaml_file(Config.FILE)
        # print(data)
        return data.get(Config.ENV, {})

    def get_base_url(self):
        return self.get_config().get('base_url', {})
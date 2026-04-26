import yaml
from pathlib import Path


config_file_path=str(Path(__file__).parent / 'env_settings.yaml')
with open(config_file_path,'r',encoding='utf-8') as f:
    data=yaml.safe_load(f)
print(data.get('production',{}))

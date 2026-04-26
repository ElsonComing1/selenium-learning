# yaml_tool.py
import yaml

class Yaml_tool(object):
    def read_yaml_file(self,file):
        with open(file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data
            # print(data)

    def write_yaml_file(self,data, file):
        with open(file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True,
                        default_flow_style=False,
                        sort_keys=False)
    


# if __name__ == "__main__":
#     yaml_tool=Yaml_tool()
#     yaml_tool.read_yaml_file('config\env_settings.yaml')
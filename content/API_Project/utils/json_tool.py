import json
from pathlib import Path
class Json_tool(object):
    def read_json_file(self, file):
        if not Path(file).exists():
            raise
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data

    def write_json_file(self, file, data):
        if not Path(file).exists():
            raise
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def append_data_to_json_file(self, file, data):
        if not Path(file).exists():
            raise
        with open(file, 'w+', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def translate_to_dict(self, data):
        return json.loads(data)

    def translate_to_json(self, data):
        return json.dumps(data, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    json_item = Json_tool()
    file_path = str(Path(__file__).parent.parent / 'data' / 'test_cases.json')
    print(json_item.read_json_file(file_path))

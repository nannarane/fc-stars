import json
import toml

with open("firebase-adminsdk.json") as f:
    python_dict = json.load(f)

# Python 딕셔너리를 TOML 문자열로 변환
toml_string = toml.dumps(python_dict)

print(toml_string)
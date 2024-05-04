import json
import base64

def decode_json_base64(encoded_key):
    encoded_key = str(encoded_key)[2:-1]
    return json.loads(base64.b64decode(encoded_key).decode('utf-8'))
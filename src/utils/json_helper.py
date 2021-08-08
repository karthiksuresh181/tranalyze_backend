import json

def read_json(JSON_PATH):
    with open(JSON_PATH)as f:
        json_data = json.load(f)
    return json_data

def write_json(JSON_PATH, json_data):
    with open(JSON_PATH, "w")as f:        
        json.dump(json_data, f)
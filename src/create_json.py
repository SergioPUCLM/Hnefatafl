import json

def creatJsonFile(fileName):
    with open(fileName, 'w') as json_file:
        json.dump(variants, json_file)

variants = [
    {
        "nombre": "Brandubh",
        "size": 7,
        "escape": [0, 6, 42, 49],
        "center": 24,
        "init_state": {
            "ID": "0",
            "blancas": [17, 23, 25, 31],
            "negras": [4, 11, 21, 22, 26, 27, 39, 46],
            "king": 24,
            "gamer": 0
        }
    },
    {
        "nombre": "placeholder",
        "size": 0,
        "escape": [0],
        "center": 0,
        "init_state": {
            "ID": "0",
            "blancas": [0],
            "negras": [0],
            "king": 0,
            "gamer": 0
        }
    }
]
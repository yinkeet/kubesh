import json
import os

def load():
    dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
    with open(dir_path + '../kubesh.json') as data:
        settings = json.load(data)
    return settings
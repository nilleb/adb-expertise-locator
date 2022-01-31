import json

def read_object(path):
    with open(path) as fd:
        return json.load(fd)

def write_object(obj, path):
    with open(path, 'w') as fd:
        json.dump(obj)

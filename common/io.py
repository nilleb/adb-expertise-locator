import json
from json import JSONEncoder


def read_object(path):
    with open(path) as fd:
        return json.load(fd)


def write_object(obj, path, cls=None):
    with open(path, "w") as fd:
        json.dump(obj, fd, cls=cls)


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

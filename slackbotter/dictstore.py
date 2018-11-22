import json
import os


class DictStore:
    def __init__(self, filename: str):
        path = os.getcwd()
        if '.json' not in filename:
            filename = filename + '.json'
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write('{}')
        self.filename = '{0}/{1}'.format(path, filename)

    def write(self, data: dict):
        with open(self.filename, 'w') as outfile:
            json.dump(data, outfile, indent=4)
        return None

    def load(self):
        with open(self.filename, 'r') as infile:
            return json.load(infile)

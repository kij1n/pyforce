import json

class JSONManager:
    def __init__(self):
        self.path = 'settings.json'
        self.s = {}
        self.load()

    def __del__(self):
        self.save()

    def load(self):
        with open(self.path, 'r') as f:
            self.s = json.load(f)

    def save(self):
        if len(self.s.items()) == 0:
            return
        with open(self.path, 'w') as f:
            json.dump(self.s, f, indent=4)

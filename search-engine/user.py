import json

class User:
    def __init__(self, id, username, mentions):
        self.id = id
        self.username = username
        self.mentions = mentions

    def add_mention(self, uid):
        if uid not in self.mentions:
            self.mentions[uid] = 0
        self.mentions[uid] += 1

    @staticmethod
    def from_json(json_str):
        user_data = json.loads(json_str)
        return User(user_data['USERID'], user_data['USERNAME'], user_data['MENTIONS'])

    def to_json(self):
        return {
            'USERID' : self.id,
            'USERNAME' : self.username,
            'MENTIONS' : self.mentions}
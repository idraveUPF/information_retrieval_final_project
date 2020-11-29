

class User:
    def __init__(self, id, username, mentions):
        self.id = id
        self.username = username
        self.mentions = mentions

    def add_mention(self, uid):
        if uid not in self.mentions:
            self.mentions[uid] = 0
        self.mentions[uid] += 1

    def to_json(self):
        return {
            'USERID' : self.id,
            'USERNAME' : self.username,
            'MENTIONS' : self.mentions}
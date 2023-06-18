class BotClientRegistry:
    def __init__(self):
        self.bot_clients = {}

    def register(self, name: str, client):
        self.bot_clients[name] = client

    def get(self, name: str):
        return self.bot_clients.get(name)

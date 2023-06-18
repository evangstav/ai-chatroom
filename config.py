import os

HOST = os.getenv("CHAT_SERVER_HOST", "0.0.0.0")
PORT = int(os.getenv("CHAT_SERVER_PORT", "9999"))

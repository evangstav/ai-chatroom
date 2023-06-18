import asyncio

import clients
import logging

from bot_client_registry import BotClientRegistry
from chat_server import ChatServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main(host: str, port: int) -> None:
    """Runs the main server loop, listening for new connections."""

    bot_registry = BotClientRegistry()
    bot_registry.register("@claude", clients.ClaudeClient())
    bot_registry.register("@chatgpt", clients.ChatGPTClient())

    chat_server = ChatServer(host, port, bot_registry)

    asyncio.run(chat_server.start_server())


if __name__ == "__main__":
    asyncio.run(main("0.0.0.0", 9999))

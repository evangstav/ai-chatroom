import asyncio
from message_utils import receive_message, send_message
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatServer:
    """ChatServer is a class that handles all chat operations."""

    def __init__(self, host: str, port: int, bot_registry):
        """Initializes ChatServer with host, port and bot_registry."""

        self.host = host
        self.port = port
        self.bot_registry = bot_registry
        self.server = None

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """
        Handles a single client connection and processes its messages.

        :param reader: StreamReader instance for reading client messages.
        :param writer: StreamWriter instance for sending messages to the client.
        """
        client_address = writer.get_extra_info("peername")
        logger.info(f"[*] New connection from {client_address}")

        try:
            while True:
                message = await receive_message(reader)
                if not message:
                    break
                logger.info(f"{client_address}: {message}")
                bot = next(
                    (bot for bot in self.bot_registry.bot_clients if bot in message),
                    None,
                )
                logger.info(f"bot used: {bot}")
                if bot:
                    message = message.replace(bot, "")
                bot_response = await self.generate_auto_response(
                    message, self.bot_registry.get(bot)
                )
                logger.info(f"auto response: {bot_response}")
                await send_message(writer, bot_response)
        except asyncio.IncompleteReadError:
            logger.warning(
                f"Disconnected before receiving complete message from {client_address}"
            )
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            await self.close_writer(writer)
            logger.info(f"[*] Connection closed with {client_address}")

    async def generate_auto_response(self, message, client=None):
        if client:
            res = await client.complete(message)
            return str(res)
            # return str(client.complete(message))
        else:
            message = message.lower()
            if "hello" in message:
                return "Hi! How can I help you?"
            elif "bye" in message:
                return "Goodbye! Have a nice day!"
            else:
                return "I'm not sure how to respond to that."

    async def close_writer(self, writer: asyncio.StreamWriter) -> None:
        writer.close()
        await writer.wait_closed()

    async def start_server(self):
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        logger.info(f"[*] Listening on {self.server.sockets[0].getsockname()}")
        async with self.server:
            await self.server.serve_forever()

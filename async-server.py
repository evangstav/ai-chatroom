import asyncio
import clients
from contextlib import asynccontextmanager
import logging

from message_utils import receive_message, send_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


bot_dict = {"@claude": clients.ClaudeClient(), "@chatgpt": clients.ChatGPTClient()}


async def generate_auto_response(message, client=None):
    if client:
        return str(client.complete(message))
    else:
        message = message.lower()
        if "hello" in message:
            return "Hi! How can I help you?"
        elif "bye" in message:
            return "Goodbye! Have a nice day!"
        else:
            return "I'm not sure how to respond to that."


async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    """Handles a single client connection and processes its messages."""
    client_address = writer.get_extra_info("peername")
    logger.info(f"[*] New connection from {client_address}")

    try:
        while True:
            message = await receive_message(reader)
            if not message:
                break
            logger.info(f"{client_address}: {message}")
            bot = next((bot for bot in bot_dict if bot in message), None)
            logger.info(f"bot used: {bot}")
            if bot:
                message = message.replace(bot, "")
            auto_response = await generate_auto_response(message, bot_dict.get(bot))
            logger.info(f"auto response: {auto_response}")
            await send_message(writer, auto_response)
    except asyncio.IncompleteReadError:
        logger.warning(f"Disconnected before receiving complete message from {client_address}")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await close_writer(writer)
        logger.info(f"[*] Connection closed with {client_address}")


async def close_writer(writer: asyncio.StreamWriter) -> None:
    writer.close()
    await writer.wait_closed()


async def main(host: str, port: int) -> None:
    """Runs the main server loop, listening for new connections."""
    async with create_server(host, port) as server:
        logger.info(f"[*] Listening on {server.sockets[0].getsockname()}")
        await server.serve_forever()


@asynccontextmanager
async def create_server(host: str, port: int) -> asyncio.AbstractServer:
    server = await asyncio.start_server(handle_client, host, port)
    try:
        yield server
    finally:
        server.close()
        await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main("0.0.0.0", 9999))

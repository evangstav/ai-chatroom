import asyncio
import clients
from contextlib import asynccontextmanager


bot_dict = {"claude": clients.ClaudeClient(), "chatgpt": clients.ChatGPTClient()}


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
    print(f"[*] New connection from {client_address}")

    try:
        while True:
            message = await read_message(reader)
            if not message:
                break
            print(f"{client_address}: {message}")
            bot = next((bot for bot in bots if bot in message), None)
            print(f"bot used: {bot}")
            if bot:
                message = message.replace(bot, "")
            auto_response = await generate_auto_response(message, bots.get(bot))
            print(f"auto response: {auto_response}")
            await send_message(writer, auto_response)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await close_writer(writer)
        print(f"[*] Connection closed with {client_address}")


async def read_message(reader: asyncio.StreamReader) -> str:
    message = await reader.read(1024)
    return message.decode("utf-8")


async def send_message(writer: asyncio.StreamWriter, message: str) -> None:
    writer.write(message.encode("utf-8"))
    await writer.drain()


async def close_writer(writer: asyncio.StreamWriter) -> None:
    writer.close()
    await writer.wait_closed()


async def main(host: str, port: int) -> None:
    """Runs the main server loop, listening for new connections."""
    async with create_server(host, port) as server:
        print(f"[*] Listening on {server.sockets[0].getsockname()}")
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

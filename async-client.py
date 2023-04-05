import asyncio
from rich.console import Console
from rich.prompt import Prompt
from rich.theme import Theme
from contextlib import asynccontextmanager

console = Console(theme=Theme({"success": "bold green", "error": "bold red"}))

@asynccontextmanager
async def connect_to_server(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()

async def send_message(writer, message):
    writer.write(message.encode('utf-8'))
    await writer.drain()

async def receive_message(reader):
    response = await reader.read(1024)
    return response.decode('utf-8')

async def main():
    console.print("[*] Python Chat Client", style="bold")

    host = "127.0.0.1"
    port = 9999

    async with connect_to_server(host, port) as (reader, writer):
        console.print(f"[*] Connected to {host}:{port}", style="success")

        while True:
            message = Prompt.ask("Enter your message (type 'exit' to quit)")
            if message.lower() == "exit":
                break

            await send_message(writer, message)
            response = await receive_message(reader)
            console.print(f"Server: {response}", style="bold")

        console.print("[*] Closing the connection", style="success")

if __name__ == "__main__":
    asyncio.run(main())

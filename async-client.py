import asyncio
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
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

def display_title():
    title = Text("Python Chat Client", style="bold white on blue", justify="center")
    console.print(Panel(title))

def display_welcome_message():
    welcome_message = Text("Welcome to the Python Chat Client!", style="bold")
    instructions = Text("Enter your messages below (type 'exit' to quit):")
    console.print(welcome_message)
    console.print(instructions)

async def main():
    display_title()
    display_welcome_message()

    host = "127.0.0.1"
    port = 9999

    async with connect_to_server(host, port) as (reader, writer):
        console.print(f"[*] Connected to {host}:{port}", style="success")

        while True:
            message = Prompt.ask("Enter your message")
            if message.lower() == "exit":
                break

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            console.print(f"[{timestamp}] You: {message}", style="bold blue")

            await send_message(writer, message)
            response = await receive_message(reader)
            console.print(f"[{timestamp}] Server: {response}", style="bold")

        console.print("[*] Closing the connection", style="success")

if __name__ == "__main__":
    asyncio.run(main())

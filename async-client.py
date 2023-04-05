import asyncio
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
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

def create_message_table():
    table = Table(show_header=False, show_lines=True, show_edge=False)
    table.add_column("Timestamp", style="dim", width=19, no_wrap=True)
    table.add_column("User", style="bold", width=10)
    table.add_column("Message")
    return table

async def main():
    display_title()
    display_welcome_message()

    host = "127.0.0.1"
    port = 9999

    async with connect_to_server(host, port) as (reader, writer):
        console.print(f"[*] Connected to {host}:{port}", style="success")

        message_table = create_message_table()

        while True:
            message = Prompt.ask("Enter your message")
            if message.lower() == "exit":
                break

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message_table.add_row(timestamp, "You:", message)

            await send_message(writer, message)
            response = await receive_message(reader)
            message_table.add_row(timestamp, "Server:", response)

            console.clear()
            display_title()
            console.print(message_table)

        console.print("[*] Closing the connection", style="success")

if __name__ == "__main__":
    asyncio.run(main())

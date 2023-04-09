import asyncio
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich.markdown import Markdown
from contextlib import asynccontextmanager
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer

from message_utils import receive_message, send_message


console = Console(theme=Theme({"success": "bold green", "error": "bold red", "username": "bold cyan", "message": "bold white"}))

@asynccontextmanager
async def connect_to_server(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        reader, writer = await asyncio.open_connection(host, port)
        yield reader, writer
    except ConnectionError:
        console.print("[!] Connection error", style="error")
        return
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()

def display_title():
    title = Text("AI Chatroom", style="bold white on blue", justify="center")
    console.print(Panel(title))

def display_welcome_message():
    welcome_message = Text("Welcome to the Python Chat Client!", style="bold")
    instructions = Text("Enter your messages below (type 'exit' to quit):")
    console.print(welcome_message)
    console.print(instructions)

def display_formatted_markdown(markdown_text: str):
    # markdown = Markdown(markdown_text, code_theme="onedark")
    markdown = Markdown(markdown_text)
    console.print(markdown)

async def shutdown(signal_, loop):
    console.print("\nShutting down gracefully...", style="success")
    tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def chat():
    display_title()
    display_welcome_message()

    host = "127.0.0.1"
    port = 9999

    async with connect_to_server(host, port) as (reader, writer):

        console.print(f"[*] Connected to {host}:{port}", style="success")

        username = input("Enter your username: ")

        history = InMemoryHistory()
        session = PromptSession(
            history=history,
            lexer=PygmentsLexer(PythonLexer),
            complete_style=CompleteStyle.READLINE_LIKE,
        )

        while True:
            message = await session.prompt_async(f"{username}> ")
            if message.lower() == "exit":
                break

            await send_message(writer, message)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            console.print(
                f"[{timestamp}] {username}: {message}", style="bold blue", justify="right"
            )

            response = await receive_message(reader)
            console.print(
                f"[{timestamp}] Server:", style="bold", justify="left"
            )
            display_formatted_markdown(response)

async def chat_wrapper():
    try:
        await chat()
    except asyncio.CancelledError:
        console.print("\nExiting...", style="error")
    except Exception as e:
        console.print(f"Error: {e}", style="error")

if __name__ == "__main__":
    try:
        asyncio.run(chat_wrapper())
    except KeyboardInterrupt:
        console.print("\nExiting...", style="error")

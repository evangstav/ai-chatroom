import asyncio
import clients


# client = clients.ClaudeClient()
client = clients.ChatGPTClient()

async def generate_auto_response(message):
    if client:
        return str(client.complete(message)) + "\n\n"
    else:
        message = message.lower()
        if "hello" in message:
            return "Hi! How can I help you?"
        elif "bye" in message:
            return "Goodbye! Have a nice day!"
        else:
            return "I'm not sure how to respond to that."


async def handle_client(reader, writer):
    """Handles a single client connection and processes its messages."""
    client_address = writer.get_extra_info('peername')
    print(f"[*] New connection from {client_address}")

    while True:
        try:
            message = await reader.read(1024)
            if not message:
                break
            message = message.decode('utf-8')
            print(f"{client_address}: {message}")

            auto_response = await generate_auto_response(message)
            print(f"Bot response: {auto_response}")
            writer.write(auto_response.encode('utf-8'))
            await writer.drain()
        except Exception as e:
            print(f"Error: {e}")
            break

    writer.close()
    await writer.wait_closed()
    print(f"[*] Connection closed with {client_address}")

async def main():
    """Runs the main server loop, listening for new connections."""
    server = await asyncio.start_server(handle_client, '0.0.0.0', 9999)

    addr = server.sockets[0].getsockname()
    print(f"[*] Listening on {addr}")

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())

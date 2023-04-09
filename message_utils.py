import asyncio

async def receive_message(reader: asyncio.StreamReader) -> str:
    header = await reader.readexactly(4)
    length = int.from_bytes(header, byteorder="big")
    message = await reader.readexactly(length)
    return message.decode("utf-8")

async def send_message(writer: asyncio.StreamWriter, message: str) -> None:
    data = message.encode("utf-8")
    header = len(data).to_bytes(4, byteorder="big")
    writer.write(header + data)
    await writer.drain()



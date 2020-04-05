import struct
import time
import asyncio
from ipaddress import IPv4Address

async def sink(source, destination):
    while True:
        data = await source.read(1024)
        if not data:
            return
        destination.write(data)
        await destination.drain()

async def handle(sr, sw):
    fmt = struct.Struct("!BBH4s")        
    request = await sr.read(fmt.size)
    version, cmd, port, ipv4 = fmt.unpack(request)
    assert version == 4
    assert cmd == 1
    identity = b""
    while not identity.endswith(b"\x00"):
        identity += await sr.read(1)
    ipv4 = str(IPv4Address(ipv4))
    print(time.time(), ipv4, port, identity)
    try:
        dr, dw = await asyncio.open_connection(host=ipv4, port=port)
    except Exception as e:
        print("error", e)
        response = fmt.pack(0, 0x5b, 0, b"\x00" * 4)
        sw.write(response)
        await sw.drain()
        raise
    else:
        response = fmt.pack(0, 0x5a, 0, b"\x00" * 4)
        sw.write(response)
        await sw.drain()
        tasks = []
        for r, w in [(sr, dw), (dr, sw)]:
            tasks.append(sink(r, w))
        await asyncio.gather(*tasks)

async def main():
    server = await asyncio.start_server(handle, host="localhost", port=8081)
    async with server:
        await server.serve_forever()

asyncio.run(main())
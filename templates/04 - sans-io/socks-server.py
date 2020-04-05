import struct
import time
import asyncio
from ipaddress import IPv4Address


def read(count):
    data = yield "read", count
    return data

def write(data):
    yield "write", data

def open_connection(host, port):
    yield "open_connection", host, port

def passthrough():
    yield "passthrough",


def protocol():
    fmt = struct.Struct("!BBH4s")
    request = yield from read(fmt.size)
    version, cmd, port, ipv4 = fmt.unpack(request)
    assert version == 4
    assert cmd == 1
    identity = b""
    while not identity.endswith(b"\x00"):
        identity += yield from read(1)
    ipv4 = str(IPv4Address(ipv4))
    print(time.time(), ipv4, port, identity)
    try:
        yield from open_connection(host=ipv4, port=port)
    except Exception as e:
        print("error", e)
        response = fmt.pack(0, 0x5b, 0, b"\x00" * 4)
        yield from write(response)
        raise
    else:
        response = fmt.pack(0, 0x5a, 0, b"\x00" * 4)
        yield from write(response)
        yield from passthrough()

async def sink(r, w):
    while True:
        data = await r.read(1024)
        if not data:
            break
        w.write(data)
        await w.drain()

async def handle(sr, sw):
    proto = protocol()
    method, value = proto.send, None
    dr = dw = None
    while True:
        action, *args = method(value)
        method = proto.send
        if action == "read":
            value = await sr.read(*args)
        elif action == "write":
            sw.write(*args)
            await sw.drain()
            value = None
        elif action == "open_connection":
            dr, dw = await asyncio.open_connection(*args)
        elif action == "passthrough":
            await asyncio.gather(
                sink(sr, dw),
                sink(dr, sw),
            )
            break
        else:
            raise ValueError(f"Unknown action {action}")


async def main():
    server = await asyncio.start_server(handle, host="localhost", port=8081)
    async with server:
        await server.serve_forever()

asyncio.run(main())

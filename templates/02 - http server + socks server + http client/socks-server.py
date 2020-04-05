import struct
import socket
import time
from ipaddress import IPv4Address
from socketserver import ThreadingTCPServer, BaseRequestHandler
from concurrent.futures import ThreadPoolExecutor, wait

def sink(source, destination):
    while True:
        data = source.recv(1024)
        if not data:
            return
        destination.sendall(data)
        
class Handler(BaseRequestHandler):
    def handle(self):
        source = self.request
        fmt = struct.Struct("!BBH4s")        
        request = source.recv(fmt.size)
        version, cmd, port, ipv4 = fmt.unpack(request)
        assert version == 4
        assert cmd == 1
        identity = b""
        while not identity.endswith(b"\x00"):
            identity += source.recv(1)
        ipv4 = str(IPv4Address(ipv4))
        print(time.time(), ipv4, port, identity)
        try:
            destination = socket.create_connection((ipv4, port))
        except Exception as e:
            print("error", e)
            response = fmt.pack(0, 0x5b, 0, b"\x00" * 4)
            source.sendall(response)
            raise
        else:
            response = fmt.pack(0, 0x5a, 0, b"\x00" * 4)
            source.sendall(response)
            with ThreadPoolExecutor(max_workers=2) as ex:
                fs = {ex.submit(sink, source, destination),
                      ex.submit(sink, destination, source)}
                wait(fs)
        
ThreadingTCPServer.allow_reuse_address = True
server = ThreadingTCPServer(("localhost", 8081), Handler)
with server:
    server.serve_forever()

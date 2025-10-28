import socket
import struct
import json

class Command:
    HELLO = 0
    GET_INFO = 1
    READY = 2
    GET_PORT = 3
    READY_FOR_STREAM = 4
    PORT_AVAILABLE = 5
    PORT_UNAVAILABLE = 6
    SEND_CLIENT_IDENTITY = 7

    CLIENT_REQUESTED_DISCONNECT = 10
    CLIENT_ERROR = 20

class ContentTypes:
    INTEGER = 1000
    JSON = 2000
    TEXT = 3000

class ServerAcknowledgements:
    ACKNOWLEDGE_HANDSHAKE_START = 100
    REQUEST_PROPOSE_PORT = 200
    REQUEST_GET_AVAILABLE_PORTS = 300
    ACKNOWLEDGE_UDP_SERVICE_START = 400
    ACKNOWLEDGE_RETURN_IDENTITY = 500
    ACKNOWLEDGE_INFO_REQUEST = 600

class HandshakeService:
    def __init__(self, addr:tuple = ("0.0.0.0", 1337), is_server:bool = True):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client = None
        self.addr = None
        self.is_server = is_server
        if not is_server:
            self.sock.connect(addr)
            self.client = self.sock
            self.addr = addr
        else:
            self.sock.bind(addr)
            self.sock.listen(1)
    
    def accept_client(self):
        if self.is_server:
            self.client, self.addr = self.sock.accept()
            print(f"Accepted connection from {self.addr}.")
            return self
        else:
            raise Exception("Cannot accept a client while being a client!")
    
    
    def listen(self):
        buf = bytes()
        while True:
            data = self.client.recv(1024)
            if not data:
                continue
            buf += data
            while len(buf) >= 12:
                cmd, cnttype, length = struct.unpack(">III", buf[:12])
                if len(buf) < 12 + length:
                    break

                content = buf[12:12 + length]
                buf = buf[12 + length:]
                if length == 0:
                    param = None
                elif cnttype == ContentTypes.TEXT:
                    param = content.decode()
                elif cnttype == ContentTypes.JSON:
                    param = json.loads(content.decode())
                elif cnttype == ContentTypes.INTEGER:
                    param = int.from_bytes(content, "big")

                return (cmd, cnttype, param)
    
    def send(self, cmd:int, param=None, cnttype=None):
        if param is None:
            content_bytes = b""
            length = 0
        else:
            if cnttype == ContentTypes.TEXT:
                content_bytes = param.encode()
            elif cnttype == ContentTypes.JSON:
                content_bytes = json.dumps(param).encode()
            elif cnttype == ContentTypes.INTEGER:
                content_bytes = int(param).to_bytes(4, 'big')
        length = len(content_bytes)

        if cnttype is None:
            fctype = ContentTypes.INTEGER if isinstance(param, int) else ContentTypes.TEXT
        else:
            fctype = cnttype
        
        packet = struct.pack(">III", cmd, fctype, length) + content_bytes
        self.client.sendall(packet)   
from Services.HandshakeService import HandshakeService, Command, ContentTypes, ServerAcknowledgements
from Services.UDPSender import start_sender
import pyaudiowpatch as pyaudio
import socket
import random

hostname = socket.gethostname()
default = pyaudio.PyAudio().get_default_wasapi_loopback()
hs = HandshakeService()
client = hs.accept_client()

def wait(command: int):
    while True:
        cmd, ctype, data = hs.listen()
        if cmd == command:
            return ctype, data

wait(Command.HELLO)
hs.send(ServerAcknowledgements.ACKNOWLEDGE_HANDSHAKE_START)
ctype, data = wait(Command.SEND_CLIENT_IDENTITY)
if ctype == ContentTypes.TEXT:
    name = data
    hs.send(ServerAcknowledgements.ACKNOWLEDGE_RETURN_IDENTITY, name, ContentTypes.TEXT)
wait(Command.GET_INFO)
hs.send(ServerAcknowledgements.ACKNOWLEDGE_INFO_REQUEST, default, ContentTypes.JSON)
wait(Command.GET_PORT)
while True:
    port = random.randint(10000, 20000)
    hs.send(ServerAcknowledgements.REQUEST_PROPOSE_PORT, port, ContentTypes.INTEGER)
    cmd, ctype, data = hs.listen()
    if cmd == Command.PORT_AVAILABLE:
        hs.send(ServerAcknowledgements.ACKNOWLEDGE_UDP_SERVICE_START)
        break
    elif cmd == Command.PORT_UNAVAILABLE:
        continue

wait(Command.READY_FOR_STREAM)
start_sender((client.addr[0], port), default)



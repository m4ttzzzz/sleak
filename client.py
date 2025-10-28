import argparse
from Services.HandshakeService import HandshakeService, Command, ContentTypes, ServerAcknowledgements
import socket
import pyaudio

parser = argparse.ArgumentParser()
parser.add_argument("-ip", type=str, help="Sets the target IPv4 address to connect to.", default="127.0.0.1")
parser.add_argument("-port", type=int, help="Sets the target port.", default=1337)
args = parser.parse_args()
pa = pyaudio.PyAudio()

hs = HandshakeService(addr=(args.ip, int(args.port)), is_server=False)
hs.send(Command.HELLO)

def wait(command):
    cmd, ctype, data = hs.listen()
    if cmd == command:
        return ctype, data

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("0.0.0.0", port))
        is_available = True
    except socket.error as e:
        is_available = False
    finally:
        sock.close()
    return is_available

wait(ServerAcknowledgements.ACKNOWLEDGE_HANDSHAKE_START)
hs.send(Command.SEND_CLIENT_IDENTITY, "Clifford", ContentTypes.TEXT)
ctype, data = wait(ServerAcknowledgements.ACKNOWLEDGE_RETURN_IDENTITY)
if ctype == ContentTypes.TEXT:
    identity = data
hs.send(Command.GET_INFO)
cnttype, data = wait(ServerAcknowledgements.ACKNOWLEDGE_INFO_REQUEST)
if cnttype == ContentTypes.JSON:
    channels = data['maxInputChannels']
    rate = int(data['defaultSampleRate'])
    ostream = pa.open(rate=rate,
                      channels=channels,
                      format=pyaudio.paInt16,
                      frames_per_buffer=512,
                      output=True)
    hs.send(Command.GET_PORT)

while True:
    cnttype, port = wait(ServerAcknowledgements.REQUEST_PROPOSE_PORT)
    if cnttype == ContentTypes.INTEGER:
        result = check_port(port)
        if result:
            hs.send(Command.PORT_AVAILABLE)
            uport = port
            break
        else:
            hs.send(Command.PORT_UNAVAILABLE)
            continue

sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2.bind(("0.0.0.0", uport))
hs.send(Command.READY_FOR_STREAM)
try:
    while True:
        adata, addr = sock2.recvfrom(512 * channels * 2)
        ostream.write(adata)
except KeyboardInterrupt:
    hs.send(Command.CLIENT_REQUESTED_DISCONNECT)
except Exception:
    hs.send(Command.CLIENT_ERROR)
finally:
    ostream.close()
    sock2.close()



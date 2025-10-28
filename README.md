# Sleak
Sleak is a Python UDP-based network audio protocol designed for streaming over LAN. 

![license](https://img.shields.io/badge/license-MIT-green)
![plogo](https://img.shields.io/badge/Python-3.10-blue)
![version](https://img.shields.io/badge/version-v0.0.1a-brightgreen)


# Features
- Dynamic port negotiation
- Lightweight
- Modular(ish) code
- Fast by default

# Implementing the protocol
Still haven't made the documentation, sorry T_T

# Using the Services
`HandshakeService` is cross-platform, but `UDPSender` is for Windows only.
```python
from Services.HandshakeService import HandshakeService, Command
hs = HandshakeService() # Starts as a TCP server by default on 127.0.0.1:1337
client = hs.accept_client()

cmd, cnttype, param = hs.listen() # Listen until client sends
if cmd == Command.HELLO:
    print("Client said hello!")

 ```
# Other Things
- Sleak is always changing, which means command names and values may change.
- Releases are made every 2 weeks or so, if I have free time.
- This project was made because I was learning sockets,
so expect instability (unless you made your own implementation.)

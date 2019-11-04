import socket
import sys

source = sys.argv[1] if len(sys.argv) == 3 else "127.0.0.1", int(sys.argv[2]) if len(sys.argv) > 2 else (int(sys.argv[1]) if len(sys.argv) == 2 else 8000)

print("Listening on %s:%d" % source)

sock = socket.socket()
sock.bind(source)
sock.listen(5)

while True:
    a, b = sock.accept()
    print("Received connection")


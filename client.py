import socket
import sys

endpoint = sys.argv[1] if len(sys.argv) == 3 else "127.0.0.1", int(sys.argv[2]) if len(sys.argv) > 2 else (int(sys.argv[1]) if len(sys.argv) == 2 else 8000)

try:
    print("Connecting to %s:%d" % endpoint)
    sock = socket.socket()
    sock.connect(endpoint)
    print("Connected to server.")
except ConnectionRefusedError:
    print("Failed to connect to server.")
finally:
    print("Disconnected from server.")
    sock.close()

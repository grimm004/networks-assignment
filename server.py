import socket
import sys
import os
from glob import glob
from datetime import datetime
import json

BOARD_DIR = "board"
LOG_FILE = "server.log"


def log(address, command, success):
    with open(LOG_FILE, "at+") as file:
        file.write("%s\t%s\t%s\t%s\n" % ("%s:%d" % address, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), command, "OK" if success else "Error"))

source = sys.argv[1] if len(sys.argv) == 3 else "127.0.0.1", int(sys.argv[2]) if len(sys.argv) > 2 else (int(sys.argv[1]) if len(sys.argv) == 2 else 8000)

def get_boards():
    return [path.split("\\")[-1].replace("_", " ") for path in glob(os.path.join(BOARD_DIR, "*"))]


def get_message(message_path):
    with open(message_path, "rt") as file:
        return file.read()


def get_messages(board_name):
    return [{"message_title": "-".join(message_path.split("\\")[-1].split("-")[2:]).replace("_", " "), "message": get_message(message_path)} for message_path in glob(os.path.join(BOARD_DIR, board_name.replace(" ", "_"), "*"))]


def create_message(board_name, message_title, message):
    board_path = os.path.join(BOARD_DIR, board_name.replace(" ", "_"))
    if not os.path.exists(board_path):
        os.makedirs(board_path)

    message_filename = "%s-%s" % (datetime.now().strftime("%d%m%Y-%H%M%S"), message_title.replace(" ", "_"))
    message_path = os.path.join(board_path, message_filename)

    with open(message_path, "wt") as file:
        file.write(message)


def handle_request(request):
    response = ""
    if request["command"] == "GET_BOARDS":
        response = json.dumps(get_boards())
    elif request["command"] == "GET_MESSAGES":
        messages = get_messages(request["board_name"])[-100:]
        response = json.dumps(messages)
    elif request["command"] == "POST_MESSAGE":
        create_message(request["board_name"], request["message_title"], request["message"])
        response = "[]"
    else:
        return None
    return response

try:
    if not os.path.exists(BOARD_DIR):
        os.makedirs(BOARD_DIR)

    print("Listening on %s:%d" % source)
    sock = socket.socket()
    sock.bind(source)
    sock.listen(5)

    while True:
        connection, address = sock.accept()
        print("Received connection from %s%d." % address)
        request = json.loads(connection.recv(1024).decode("utf-8"))
        response = handle_request(request)
        if response is not None:
            connection.send(response.encode("utf-8"))
        log(address, request["command"], response is not None)
        connection.close()

except OSError:
    print("Error: Port %d already in use." % source[1])

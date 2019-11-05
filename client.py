import socket
import sys
import json

socket.setdefaulttimeout(10)
endpoint = sys.argv[1] if len(sys.argv) == 3 else "127.0.0.1", int(sys.argv[2]) if len(sys.argv) > 2 else (int(sys.argv[1]) if len(sys.argv) == 2 else 8000)

def encode_command(command, **kwargs):
    kwargs["command"] = command
    return json.dumps(kwargs).encode()


def send_command(sock, command, **kwargs):
    sock.send(encode_command(command, **kwargs))


def await_response(sock):
    return json.loads(sock.recv(1024).decode("utf-8"))


def run_command(command, **kwargs):
    with socket.socket() as sock:
        sock.connect(endpoint)
        send_command(sock, command, **kwargs)
        return await_response(sock)


def get_boards():
    return run_command("GET_BOARDS")


def get_messages(board_name):
    return run_command("GET_MESSAGES", board_name = board_name)


def post_message(board_name, message_title, message):
    run_command("POST_MESSAGE", board_name = board_name, message_title = message_title, message = message)


try:
    boards = get_boards()
    print("\n".join(["%d. %s" % (i + 1, boards[i]) for i in range(len(boards))]))
    print("Available Commands: '<board number>', 'POST' or 'QUIT'.")
    while True:
        request = input("> ")
        if request.isdigit():
            selected = int(request)
            if 0 < selected <= len(boards):
                messages = get_messages(boards[selected - 1])
                if len(messages) == 0:
                    print("No messages in %s." % boards[selected - 1])
                else:
                    print("Messages in %s:" % boards[selected - 1])
                    print("\n".join("%s: %s" % (message["message_title"], message["message"]) for message in messages))
            else:
                print("Invalid board selection.")
                continue
        elif request == "POST":
            request = input("Enter board number:\n> ")
            if request.isdigit():
                selected = int(request)
                if 0 < selected <= len(boards):
                    post_message(boards[selected - 1], input("Enter message title:\n> "), input("Eneter message:\n> "))
                else:
                    print("Invalid board selection.")
                    continue
            else:
                print("Invalid board selection.")
        elif request == "QUIT":
            break
        elif request == "":
            continue
        else:
            print("Invalid selection.\nAvailable Commands: '<board number>', 'POST' or 'QUIT'.")
except ConnectionRefusedError:
    print("Error: Failed to connect to server.")
except socket.timeout:
    print("Error: Socket timed out")
finally:
    print("Exiting...")

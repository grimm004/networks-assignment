import socket
import sys
import json

# Set the default timeout of any created sockets to 10 seconds (as required)
socket.setdefaulttimeout(10)
# Access the supplied command line arguments (if one is supplied treat it as a port, if two are supplied treat as host and port) default to 127.0.0.1:8000
endpoint = sys.argv[1] if len(sys.argv) == 3 else "127.0.0.1", int(sys.argv[2]) if len(sys.argv) > 2 else (int(sys.argv[1]) if len(sys.argv) == 2 else 8000)

def encode_command(command, **kwargs):
    # Encode a command with parameters into JSON
    # Take the keyword args supplied as a dictionary and add the command name to it
    kwargs["command"] = command
    # Encode and return the utf-8 encoded JSON
    return json.dumps(kwargs).encode("utf-8")


def send_command(sock, command, **kwargs):
    # Encode the supplied command and arguments and send it
    sock.send(encode_command(command, **kwargs))


def await_response(sock):
    try:
        # Decode the received data and try deserialise and return it
        return json.loads(sock.recv(65536).decode("utf-8"))
    except ValueError:
        # A value error means the JSON decoder encountered a corrupt or empty string
        return None


def run_command(command, **kwargs):
    # Open a TCP socket
    with socket.socket() as sock:
        sock.settimeout(10)
        # Connect to the supplied host and port
        sock.connect(endpoint)
        # Send the supplied command
        send_command(sock, command, **kwargs)
        # Once a response has been recieved, return it
        return await_response(sock)


def get_boards():
    # Run the GET_BOARDS command and return the result
    return run_command("GET_BOARDS")


def get_messages(board_name):
    # Run the GET_MESSAGES command and return the result
    return run_command("GET_MESSAGES", board_name = board_name)


def post_message(board_name, message_title, message):
    # Run the POST_MESSAGE command and return the result
    return run_command("POST_MESSAGE", board_name = board_name, message_title = message_title, message = message)


if __name__ == "__main__":
    try:
        # Fetch the list of available boards
        response = get_boards()
        if not response["success"]:
            print("Error: No message boards, exiting...")
            exit()
        boards = response["boards"]
        # If there is an error collecting the boards output an error and exit
        if boards is None:
            print("Error fetching boards.")
            exit()
        # Output the formatted list of boards
        print("\n".join(["%d. %s" % (i + 1, boards[i]) for i in range(len(boards))]))
        print("Available Commands: '<board number>', 'POST' or 'QUIT'.")
        # Infinately loop to continuously handle user requests
        while True:
            # Fetch the users input
            request = input("> ")
            # If the input is a non-negative number
            if request.isdigit():
                # Cast it from a string to an integer
                selected = int(request)
                # Check its within the range of board numbers
                if 0 < selected <= len(boards):
                    # Get the messages for the corresponding board
                    response = get_messages(boards[selected - 1])
                    if response["success"]:
                        # If the messages could not be retrieved print an error
                        if response["messages"] is None:
                            print("Error fetching messages.")
                            continue
                        # If there are no messages, output a warning
                        if len(response["messages"]) == 0:
                            print("No messages in %s." % boards[selected - 1])
                        else:
                            # If there are messages, output them
                            print("Messages in %s:" % boards[selected - 1])
                            print("\n".join("%s: %s" % (message["message_title"], message["message"]) for message in response["messages"]))
                    else:
                        print("Error: %s" % response["message"])
                else:
                    print("Invalid board selection.")
                    continue
            # If the input is a POST request
            elif request == "POST":
                # Request the user to input the desired board to post to
                request = input("Enter board number:\n> ")
                # Check its a valid board ID (as done above)
                if request.isdigit():
                    selected = int(request)
                    if 0 < selected <= len(boards):
                        # If all is valid, fetch message title and message input and post it to the server
                        response = post_message(boards[selected - 1], input("Enter message title:\n> "), input("Eneter message:\n> "))
                        if response["success"]:
                            print("Message posted.")
                        else:
                            print("Error posting message: %s" % response["message"])
                            continue
                    else:
                        print("Invalid board selection.")
                        continue
                else:
                    print("Invalid board selection.")
            # If the input is a QUIT request
            elif request == "QUIT":
                # Leave the while loop
                break
            elif request == "":
                continue
            else:
                print("Invalid selection.\nAvailable Commands: '<board number>', 'POST' or 'QUIT'.")
    except ConnectionRefusedError:
        print("Error: Failed to connect to server.")
    except socket.timeout:
        # Output an error if the socket times out and quit
        print("Error: Socket timed out")
    except ConnectionResetError:
        # Output an error if the socket cannot connect and quit
        print("Error: Connection reset")
    finally:
        print("Exiting...")

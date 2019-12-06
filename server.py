import socket
import sys
import os
from glob import glob
from datetime import datetime
import json

BOARD_DIR = "board"
LOG_FILE = "server.log"


def log(address, command, success):
    # Open the log file for text appending
    with open(LOG_FILE, "at+") as file:
        # Write the required information to the log file
        file.write("%s\t%s\t%s\t%s\n" % ("%s:%d" % address, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), command, "OK" if success else "Error"))

# Access the supplied command line arguments (if one is supplied treat it as a port, if two are supplied treat as host and port) default to 127.0.0.1:8000
source = sys.argv[1] if len(sys.argv) == 3 else "127.0.0.1", int(sys.argv[2]) if len(sys.argv) > 2 else (int(sys.argv[1]) if len(sys.argv) == 2 else 8000)


def get_boards():
    # Use list comprehention and string manipulation to extract the name of each board from the list of file names in the board directory
    return [path.split("\\")[-1].replace("_", " ") for path in glob(os.path.join(BOARD_DIR, "*"))]


def get_message(message_path):
    # Open the message file for text reading
    with open(message_path, "rt") as file:
        # Read and return the contents
        return file.read()


def get_messages(board_name):
    # Use list comprehention and string manipulation to extract the data for the last 100 messages from the files in the boards directory
    return [{"message_title": "-".join(message_path.split("\\")[-1].split("-")[2:]).replace("_", " "), "message": get_message(message_path)} for message_path in glob(os.path.join(BOARD_DIR, board_name.replace(" ", "_"), "*"))]


def create_message(board_name, message_title, message):
    # Access the path of the board being posted to
    board_path = os.path.join(BOARD_DIR, board_name.replace(" ", "_"))
    # Create the path if it does not exist
    if not os.path.exists(board_path):
        os.makedirs(board_path)

    # Access the filename and path of the message to be posted
    message_filename = "%s-%s" % (datetime.now().strftime("%d%m%Y-%H%M%S"), message_title.replace(" ", "_"))
    message_path = os.path.join(board_path, message_filename)

    # Open the file (to have text written to)
    with open(message_path, "wt") as file:
        # Write the message to the file
        file.write(message)


# Function to hanle incoming requests
def handle_request(request):
    # If the request dictionary does not include a dictionary
    if "command" not in request:
        return (False, None)
    response = ""
    # GET_BOARDS request
    if request["command"] == "GET_BOARDS":
        response = json.dumps({"success": True, "boards": get_boards()})
    # GET_MESSAGES request
    elif request["command"] == "GET_MESSAGES":
        # Check all the required field is supplied
        if "board_name" not in request:
            return (False, None)
        # Check the board exists
        if request["board_name"] not in get_boards():
            return (False, json.dumps({"success": False, "message": "Invalid board name."}))
        messages = get_messages(request["board_name"])[-100:]
        response = json.dumps({"success": True, "messages": messages})
    # POST_MESSAGE request
    elif request["command"] == "POST_MESSAGE":
        # Check all the required fields are supplied
        if not ("board_name" in request and "message_title" in request and "message" in request):
            return (False, None)
        # Check the board exists
        if request["board_name"] not in get_boards():
            return (False, json.dumps({"success": False, "message": "Invalid board name."}))
        create_message(request["board_name"], request["message_title"], request["message"])
        response = json.dumps({"success": True})
    else: return (False, None)
    return (True, response)

# If the module is not being imported
if __name__ == "__main__":
    if len(get_boards()) == 0:
        print("Error: No message boards defined, exiting...")
        exit()
    try:
        # If the board directory does not exist, create it
        if not os.path.exists(BOARD_DIR):
            os.makedirs(BOARD_DIR)

        # Create a TCP socket and bind to the provided host and port
        print("Listening on %s:%d" % source)
        sock = socket.socket()
        sock.bind(source)
        # Allow a queue of 10 incoming clients
        sock.listen(10)

        # Infinite loop to handle each request (and connection)
        while True:
            try:
                # Accept an incoming TCP connection
                connection, address = sock.accept()
                # Decode the received decoded JSON request 
                request = json.loads(connection.recv(65536).decode("utf-8"))
                # Handle the request
                success, response = handle_request(request)
                # If a response is defined, send it back, else send back an error
                connection.send(response.encode("utf-8") if response != None else json.dumps({"success": False, "message": "Invalid command or syntax."}).encode("utf-8"))
                # Log the request
                log(address, request["command"], success)
            except ValueError as e:
                # A ValueError occurs when an empty string is provided to the JSON deserialiser
                print("Error while decoding message:", e)
                log(address, "UNKNOWN", False)
            except OSError as e:
                # An OSError occurs when the socket encounters an exception
                print("A socket error occurred:", e)
                log(address, "UNKNOWN", False)
            finally:
                # Close the connection
                connection.close()

    except OSError as e:
        # An OSError occurrs when an invalid host IP or port is supplied or a port has already been bound to
        print("Error: Could not bind to %s, %s" % ("%s:%d" % source, e))
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    finally:
        print("Exiting...")

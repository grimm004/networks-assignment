import client
import threading
import time

def test():
    print(client.get_boards())
    print(client.get_messages("My other test board"))
    print(client.get_messages("My test board"))
    print(client.get_messages("test wrong"))
    print(client.post_message("My test board", "Test %.4f" % time.time(), "This is a test message."))

while True:
    threading.Thread(target=test).start()
    time.sleep(1)

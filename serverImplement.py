import socket
import threading
import sys
import traceback
import selectors
import os
import serverLib

host = socket.gethostbyname(socket.gethostname())
port = 65432
SIZE = 1024 * 4
FORMAT = "utf-8"


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        message = serverLib.Message(conn, addr)
        message.read()
        # print("start writing")
        connected = message.write()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()
print(f"Listening on {(host, port)}")

flag = True
while flag:
    conn, addr = server.accept()
    print(f"Accepted connection from {addr}")
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

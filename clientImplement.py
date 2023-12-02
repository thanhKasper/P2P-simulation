import threading
import socket
import json
import traceback
import clientLib

server_ip = "192.168.56.1"
server_port = 65432


def validate_request(user_input):
    if len(user_input) == 0 or len(user_input) > 3:
        return -1
    elif len(user_input) == 1:
        if user_input[0] == "GET_INFO":
            return 5
        elif user_input[0] == "LEAVE":
            return 6
        return -1
    elif len(user_input) == 2:
        if user_input[0] == "REMOVE":
            return 2
        elif user_input[0] == "FETCH":
            return 4
        return -1
    elif len(user_input) == 3:
        if user_input[0] == "SEND":
            return 1
        elif user_input[0] == "UPDATE":
            return 3
    return -1


def forming_request(client_name):
    user_input = input("> ")
    user_input = user_input.split()
    act = validate_request(user_input)
    if act == -1:
        print("Invalid syntax")
        return
    new_request = dict(
        type="text/json",
        encoding="utf-8",
        content=dict(client_name=client_name, action=user_input[0])
    )
    if act == 5 or act == 6:
        return new_request
    if act == 1 or act == 3:
        new_request["content"]["path"] = user_input[1]
        new_request["content"]["file_name"] = user_input[2]
        return new_request
    new_request["content"]["file_name"] = user_input[1]
    return new_request


def start_connection(host, port, connection_request):
    addr = (host, port)
    print(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect_ex(addr)
    message = clientLib.Message(sock, addr, connection_request)
    message.write()
    message.read()
    return sock, addr


username = input("Please enter your username: ")
# create a request to connect to server
requestConnect = dict(
    type="text/json",
    encoding="utf-8",
    content=dict(client_name=username, action="CONNECT")
)
# create a socket to send and receive data from the server
client_socket, server_addr = start_connection(server_ip, server_port, requestConnect)

# file_list = [
#     {
#         "client_name": "Thanh",
#         "IP": "192.168.1.76",
#         "port": 12345,
#         "path": ['D:/dir1/dir2'],
#         "file_name": ["file1.txt"]
#     },
#     {
#         "client_name": "Thanh2",
#         "IP": "10.0.1.23",
#         "port": 37581,
#         "path": ["D:/a/b/e"],
#         "file_name": ["file1.txt"]
#     }
# ]

flag = True
while flag:
    request = forming_request(username)
    formatted_request = clientLib.Message(client_socket, server_addr, request)
    formatted_request.write()
    data = formatted_request.read()
    if request['content']['action'] == 'GET_INFO':
        if not (data is None):
            print(f'UserInformation: {data}')
    elif request['content']['action'] == 'FETCH':
        if not (data is None):
            print(f'Clients holding {request["content"]["file_name"]}: {data}')
    elif request['content']['action'] == 'LEAVE':
        request_message.close()
        break

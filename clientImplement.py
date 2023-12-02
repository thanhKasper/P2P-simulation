import threading
import socket
import json
import traceback
import clientLib

server_addr = "192.168.56.1"
port = 65432
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def validateRequest(input):
    if len(input) == 0 or len(input) > 3:
        return -1
    elif len(input) == 1:
        if input[0] == "GET_INFO":
            return 5
        elif input[0] == "LEAVE":
            return 6
        return -1
    elif len(input) == 2:
        if input[0] == "REMOVE":
            return 2
        elif input[0] == "FETCH":
            return 4
        return -1
    elif len(input) == 3:
        if input[0] == "SEND":
            return 1
        elif input[0] == "UPDATE":
            return 3
    return -1


def formingRequest(clientName):
    userInput = input("> ")
    userInput = userInput.split()
    act = validateRequest(userInput)
    if act == -1:
        print("Invalid syntax")
        return
    request = dict(
        type="text/json",
        encoding="utf-8",
        content=dict(client_name=clientName, action=userInput[0])
    )
    if act == 5 or act == 6:
        return request
    if act == 1 or act == 3:
        request["content"]["path"] = userInput[1]
        request["content"]["file_name"] = userInput[2]
        return request
    request["content"]["file_name"] = userInput[1]
    return request


def start_connection(host, port, request):
    addr = (host, port)
    print(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect_ex(addr)
    message = clientLib.Message(sock, addr, request)
    message.write()
    message.read()
    return sock, addr


def Welcome():
    username = input("Please enter your username: ")
    return username


username = Welcome()
requestConnect = dict(
    type="text/json",
    encoding="utf-8",
    content=dict(client_name=username, action="CONNECT")
)
sock, addr = start_connection(server_addr, port, requestConnect)

flag = True
while flag:
    request = (formingRequest(username))
    message = clientLib.Message(sock, addr, request)
    message.write()
    data = message.read()
    if request['content']['action'] == 'GET_INFO':
        if not (data is None):
            print(f'UserInformation: {data}')
    elif request['content']['action'] == 'FETCH':
        if not (data is None):
            print(f'Clients holding {request["content"]["file_name"]}: {data}')
    elif request['content']['action'] == 'LEAVE':
        message.close()
        break

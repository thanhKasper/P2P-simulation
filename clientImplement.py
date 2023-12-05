import threading
import socket
import json
import traceback
import clientLib
import sys
server_addr = "192.168.1.78"
port = 65432
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class Client:
    def __init__(self,serverAddress, serverPort,userName):
        self.sAddr = serverAddress
        self.sPort = serverPort
        self.socket = None
        self.username = userName
    def __del__(self):
        self.socket = None
    def validateRequest(self,input):
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
    def formingRequest(self,input):
        userInput = input
        userInput = userInput.split()
        act = self.validateRequest(userInput)
        if act == -1:
            print("Invalid syntax")
            return None
        request = dict(
            type="text/json",
            encoding="utf-8",
            content=dict(client_name=self.username, action=userInput[0])
        )
        if act == 5 or act == 6:
            return request
        if act == 1 or act == 3:
            request["content"]["path"] = userInput[1]
            request["content"]["file_name"] = userInput[2]
            return request
        request["content"]["file_name"] = userInput[1]
        return request
    def start_connection(self):
        if not (self.socket is None):
            raise ValueError(("Thread trying to start another socket to server."))
        addr = (self.sAddr, self.sPort)
        print(f"Starting connection to {addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect_ex(addr)

        request = dict(
            type="text/json",
            encoding="utf-8",
            content=dict(client_name=self.username, action="CONNECT")
        )
        message = clientLib.Message(sock, addr, request)
        message.write()
        message.read()
        self.socket = sock
    def handleRequest(self,input):
        if self.socket is None:
            raise ValueError("Socket does not exist")
        request = self.formingRequest(input)
        message = clientLib.Message(self.socket, (self.sAddr, self.sPort), request)
        message.write()
        data = message.read()
        if request['content']['action'] == 'GET_INFO':
            if not (data is None):
                return data
            else:
                raise ValueError(f"Data for client {self.username} does not exist")
        elif request['content']['action'] == 'FETCH':
            if not (data is None):
                return data
            else: 
                raise ValueError(f"Fetch data for client {self.username} does not exist")
        elif (request['content']['action'] == 'LEAVE'):
            message.close()
        




def Welcome():
    username = input("Please enter your username: ")
    return username


username = Welcome()
client = Client(server_addr,port,username)
client.start_connection()
client.handleRequest("LEAVE")

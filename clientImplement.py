import os.path
import threading
import socket
import clientLib

file_list = [
    {
        "client_name": "Thanh",
        "IP": "192.168.56.1",
        "port": 12345,
        "path": ['D:/School Reference/HK231/Database'],
        "file_name": ["Assignment 1 task.pdf"]
    },
    {
        "client_name": "Thanh2",
        "IP": "192.168.56.1",
        "port": 37581,
        "path": ["D:/folder1"],
        "file_name": ["ocean.png"]
    }
]

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
        self.handle_downloading_thread = threading.Thread(target=create_downloading_process, daemon=True)
        self.handle_downloading_thread.start()
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

    def send_file_to_client(self, client_socket, file_path):
        # Prepare and send file
        file = open(file_path, "rb")
        file_data_binary = file.read()
        client_socket.sendall(file_data_binary)
        print("File sent to client")
        file.close()

    def download_file(self, server_socket, file_path, file_name):
        full_path = file_path + '/' + file_name
        server_socket.send(full_path.encode(FORMAT))
        file_size = server_socket.recv(1024).decode(FORMAT)
        print(f"Size of a file: {file_size}")
        received_file_size = int(file_size)
        file = open(server_filename, "wb")
        data_received = server_socket.recv(received_file_size)
        file.write(data_received)
        file.close()
        print("File downloaded")

    # Accept one client socket that want to communicate with server
    def socket_accept(self, server_socket):
        while True:
            conn, addr = server_socket.accept()
            conn.send("Connected to server".encode(FORMAT))
            file_path = conn.recv(1024).decode(FORMAT)
            file_len = os.path.getsize(file_path)
            conn.send(str(file_len).encode(FORMAT))
            handle_client_thread = threading.Thread(target=send_file_to_client, args=(conn, file_path))
            handle_client_thread.start()

    # Create a new port for sending downloaded file to other client
    def create_downloading_process():
        print("Create a thread for downloading file")
        my_ip = socket.gethostbyname(socket.gethostname())
        downloading_port = 50000
        handle_downloading_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        handle_downloading_socket.bind((my_ip, downloading_port))
        handle_downloading_socket.listen()
        socket_accept(handle_downloading_socket)

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
                print(f'Clients holding {request["content"]["file_name"]}: {data}')
                server_name = data[0]["client_name"]
                server_ip = data[0]["IP"]
                server_port = data[0]["port"]
                server_path = data[0]["path"][0]
                server_filename = data[0]["file_name"][0]
                print(server_name, server_ip, server_port, server_path, server_filename)
                get_file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                get_file_socket.connect((server_ip, 50000))
                # Receive info whether connect to server or not
                print(get_file_socket.recv(1024).decode(FORMAT))
                # request downloading file
                download_file(get_file_socket, server_path, server_filename)
                get_file_socket.close()
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

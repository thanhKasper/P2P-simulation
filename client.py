import threading
import socket
import json
import time


class ClientController:
    def __init__(self, server_ip, server_port):
        self.username = ""
        self.server_addr = "192.168.56.1"
        self.server_ip = server_ip
        self.server_port = server_port
        self.is_connected = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self, hostname):
        self.username = hostname
        print(f"Connect to server as {self.username}")
        self.client_socket.connect((self.server_addr, self.server_port))
        self.client_socket.send(self.username.encode())
        msg = self.client_socket.recv(1024).decode()
        print(msg)
        self.is_connected = True

    def leave_server(self):
        self.client_socket.close()
        self.is_connected = False

    def add_file_info(self, pathname, filename):
        self.client_socket.send("SEND".encode())
        self.client_socket.send((pathname + '@' + filename).encode())
        msg = self.client_socket.recv(1024).decode()
        print(msg)

    def remove_file(self, filename):
        self.client_socket.send("REMOVE".encode())
        self.client_socket.send(filename.encode())
        msg = self.client_socket.recv(1024).decode()
        print(msg)

    def update_path_name(self, new_path, filename):
        self.client_socket.send("UPDATE".encode())
        self.client_socket.send((new_path + '@' + filename).encode())
        msg = self.client_socket.recv(1024).decode()
        print(msg)

    def fetch_file(self, filename):
        self.client_socket.send("FETCH".encode())
        self.client_socket.send(filename.encode())
        file_list = self.client_socket.recv(2048).decode()
        file_list = json.loads(file_list)
        return file_list['client']

    def get_my_info(self):
        self.client_socket.send("GET_INFO".encode())
        client_info = self.client_socket.recv(2048).decode()
        if client_info == '-1':
            return "No file established"
        else:
            client_info = json.loads(client_info)
            return client_info['client_info']

# print(fetch_file("image.png")[0])
# add_file_info('D:/NGUYEN/DAI HOC/Book/Semester 5/COMPUTER NETWORKS/Assignment1' , "image.png")
# update_path_name('D:/', "image1.png")

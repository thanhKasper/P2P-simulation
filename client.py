import threading
import socket
import json


server_addr = "192.168.56.1"
port = 23578
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect_to_server(as_name):
    client_socket.connect((server_addr, port))
    client_socket.send()


def leave_server():
    client_socket.close()


def add_file_info(pathname, filename):
    client_socket.send("SEND ".encode())
    client_socket.send((pathname + ' ' + filename).encode())


def remove_file(filename):
    client_socket.send("REMOVE ".encode())
    client_socket.send(filename.encode())


def update_path_name(new_path, filename):
    client_socket.send("UPDATE ".encode)
    client_socket.send(new_path + ' ' + filename)


def fetch_file(filename):
    client_socket.send("FETCH ".encode())
    client_socket.send(filename.encode())
    file_list = client_socket.recv(2048).decode()
    file_list = json.loads(file_list)
    return file_list


def get_my_info():
    client_socket.send("GET_INFO".encode())
    client_info = client_socket.recv(2048).decode()
    return client_info


connect_to_server()
# add_file_info("D:/myFile", "readme.txt")
# print(res)

mydict = {"name": "Thanh", "age": 18}
jsonFile = json.dumps(mydict)
client_socket.send(jsonFile.encode())


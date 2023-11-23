import threading
import socket
import json
import time


server_addr = "192.168.1.6"
port = 23578
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect_to_server(as_name):
    client_socket.connect((server_addr, port))
    client_socket.send((as_name).encode())
    msg = client_socket.recv(1024).decode()
    print(msg)

def leave_server():
    client_socket.close()


def add_file_info(pathname, filename):
    client_socket.send("SEND".encode())
    client_socket.send((pathname + '@' + filename).encode())
    msg = client_socket.recv(1024).decode()
    print(msg)


def remove_file(filename):
    client_socket.send("REMOVE".encode())
    client_socket.send((filename).encode())
    msg = client_socket.recv(1024).decode()
    print(msg)


def update_path_name(new_path, filename):
    client_socket.send("UPDATE".encode())
    client_socket.send((new_path + '@' + filename).encode())
    msg = client_socket.recv(1024).decode()
    print(msg)


def fetch_file(filename):
    client_socket.send("FETCH".encode())
    client_socket.send(filename.encode())
    file_list = client_socket.recv(2048).decode()
    file_list = json.loads(file_list)

    return file_list['client']


def get_my_info():
    client_socket.send("GET_INFO".encode())
    client_info = client_socket.recv(2048).decode()
    if client_info == '-1':
        return "No file established"
    else:
        client_info = json.loads(client_info)
        return client_info['client_info']


connect_to_server("Bao Nguyen")


# print(fetch_file("image.png")[0])
# add_file_info('D:/NGUYEN/DAI HOC/Book/Semester 5/COMPUTER NETWORKS/Assignment1' , "image.png")
# update_path_name('D:/', "image1.png")
print(get_my_info())

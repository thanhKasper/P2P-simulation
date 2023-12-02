import os.path
import threading
import socket
import clientLib

FORMAT = "utf-8"
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
# client_socket, server_addr = start_connection(server_ip, server_port, requestConnect)

file_list = [
    {
        "client_name": "Thanh",
        "IP": "192.168.56.1",
        "port": 12345,
        "path": ['D:\\School Reference\\HK231\\Database'],
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


def send_file_to_client(client_socket, file_path):
    # Prepare and send file
    file = open(file_path, "rb")
    file_data_binary = file.read()
    client_socket.sendall(file_data_binary)
    print("File sent to client")
    file.close()


def download_file(server_socket, file_path, file_name):
    full_path = file_path + '/' + file_name
    get_file_socket.send(full_path.encode(FORMAT))
    file_size = get_file_socket.recv(1024).decode(FORMAT)
    print(f"Size of a file: {file_size}")
    received_file_size = int(file_size)
    file = open(server_filename, "wb")
    data_received = get_file_socket.recv(received_file_size)
    file.write(data_received)
    file.close()
    print("File downloaded")


# Accept one client socket that want to communicate with server
def socket_accept(server_socket):
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


handle_downloading_thread = threading.Thread(target=create_downloading_process, daemon=True)
handle_downloading_thread.start()

flag = True
while flag:
    print(socket.gethostbyname(socket.gethostname()))
    request = forming_request(username)
    # formatted_request = clientLib.Message(client_socket, server_addr, request)  # adjusted request for sending
    # formatted_request.write()
    # data = formatted_request.read()
    data = file_list
    if request['content']['action'] == 'GET_INFO':
        if not (data is None):
            print(f'UserInformation: {data}')
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
    elif request['content']['action'] == 'LEAVE':
        formatted_request.close()
        break

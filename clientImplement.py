import os.path
import threading
import socket
import clientLib


server_addr = "192.168.1.78"
port = 65432
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Client:
    def __init__(self, server_address, server_port):
        self.sAddr = server_address  # Server IP address
        self.sPort = server_port     # Server port
        self.socket = None           # the socket to connect to server
        self.username = ""           # username to distinguish between clients
        # Create another thread that waiting for request to send file to clients
        self.handle_downloading_thread = threading.Thread(target=self.create_downloading_process, daemon=True)
        self.handle_downloading_thread.start()
        self.FORMAT = 'utf-8'
        self.is_connected = False

    def __del__(self):
        self.socket = None

    def validate_request(self, input):
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

    def forming_request(self, input):
        userInput = input
        userInput = userInput.split()
        act = self.validate_request(userInput)
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
            raise ValueError("Thread trying to start another socket to server.")
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
        self.is_connected = True

    # Client download file from another client
    def download_file(self, server_socket, file_path):
        server_socket.send(file_path.encode(self.FORMAT))
        file_size = server_socket.recv(1024).decode(self.FORMAT)
        print(f"Size of a file: {file_size}")
        received_file_size = int(file_size)
        filename = file_path[file_path.rfind('/')+1:]
        file = open(filename, "wb")
        data_received = server_socket.recv(received_file_size)
        file.write(data_received)
        file.close()
        print("File downloaded")

    # These functions belows apply for a client that works like a server to send file to another client
    def send_file_to_client(self, sending_socket, file_path):
        # Prepare and send file
        file = open(file_path, "rb")
        file_data_binary = file.read()
        sending_socket.sendall(file_data_binary)
        print("File sent to client")
        file.close()

    # Accept one client socket that want to communicate with server
    def socket_accept_client(self, server_socket):
        while True:
            # conn is a socket used to communicate with client
            conn, addr = server_socket.accept()
            conn.send("Connected to server".encode(self.FORMAT))
            file_path = conn.recv(1024).decode(self.FORMAT)
            print(f"Server receive file path {file_path}")
            file_len = os.path.getsize(file_path)
            print(f"Server side size of a file: {file_len}")
            conn.send(str(file_len).encode(self.FORMAT))
            handle_client_thread = threading.Thread(target=self.send_file_to_client, args=(conn, file_path))
            handle_client_thread.start()

    # Create a new port for sending downloaded file to other client
    def create_downloading_process(self):
        print("Create a thread for downloading file")
        my_ip = socket.gethostbyname(socket.gethostname())
        downloading_port = 50000
        handle_downloading_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        handle_downloading_socket.bind((my_ip, downloading_port))
        handle_downloading_socket.listen()
        self.socket_accept_client(handle_downloading_socket)

    # raw_request: Request of type string like 'FETCH path file'
    def handle_request(self, raw_request):
        if self.socket is None:
            raise ValueError("Socket does not exist")
        request = self.forming_request(raw_request)
        message = clientLib.Message(self.socket, (self.sAddr, self.sPort), request)
        message.write()
        data = message.read()
        # data = [
        #     {
        #         "client_name": "Thanh",
        #         "IP": "192.168.56.1",
        #         "port": 12345,
        #         "path": ['D:/myFolder/anotherFolder'],
        #         "file_name": ["CN_assignment.txt"]
        #     },
        #     {
        #         "client_name": "Thanh2",
        #         "IP": "192.168.56.1",
        #         "port": 37581,
        #         "path": ["D:/diffFolder"],
        #         "file_name": ["CN_assignment.txt"]
        #     }
        # ]
        if request['content']['action'] == 'GET_INFO':
            if not (data is None):
                return data
            else:
                raise ValueError(f"Data for client {self.username} does not exist")
        elif request['content']['action'] == 'FETCH':
            if not (data is None):
                # print(f'Clients holding {request["content"]["file_name"]}: {data}')
                # print("Currently there are ", len(data), " having the file you want to download")
                # choice = int(input("Which one you want to choose: "))
                #
                # info = data[choice]
                # server_ip = info["IP"]
                # path = info["path"][0]
                # filename = info["file_name"][0]
                #
                # full_path = path + "/" + filename
                # print(full_path)
                # get_file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # get_file_socket.connect((server_ip, 50000))
                # # Receive info whether connect to server or not
                # print(get_file_socket.recv(1024).decode(self.FORMAT))
                # # request downloading file
                # self.download_file(get_file_socket, full_path)
                # get_file_socket.close()
                return data
            else:
                raise ValueError(f"Fetch data for client {self.username} does not exist")
        elif request['content']['action'] == 'LEAVE':
            message.close()
            self.socket.close()
            self.is_connected = False
        elif request['content']['action'] == 'SEND':
            print("[SEND] sending file to server")
            if data is not None:
                print(data)



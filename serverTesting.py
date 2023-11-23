import socket
import json
import threading
    

server_ip = socket.gethostbyname(socket.gethostname())
server_port = 23578
print(server_ip)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_ip, server_port))

while True:
    server.listen()
    client_conn, client_addr = server.accept()
    msg = client_conn.recv(2048).decode('ascii')
    jsonObj = json.loads(msg)
    # msg_analysis = msg.split(' ')
    # if msg_analysis[0] == "SEND_FILE":
    #     client_conn.send("You want to upload file to server, is that right?".encode())
    print(jsonObj['name'])

    client_conn.close()





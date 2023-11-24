import threading
import socket
import json
import traceback
import clientLib

server_addr = "192.168.1.76"
port = 65432
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

request = dict(
    type="text/json",
    encoding="utf-8",
    content=dict(action="SEND",file_name="MinhDang",path="path....")
)
request1 = dict(
    type="text/json",
    encoding="utf-8",
    content=dict(action="FETCH",file_name="MinhDang")
)
def start_connection(host, port, request):
    addr = (host, port)
    print(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect_ex(addr)
    message = clientLib.Message( sock, addr, request1)
    message.write()
    message.read()
    
start_connection(server_addr, port, request)
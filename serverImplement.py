import socket
import threading
import sys
import traceback
import selectors
import os
import serverLib
import select
host = socket.gethostbyname(socket.gethostname())
port = 65432




def handle_client(conn, addr,stop):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        if stop():
            print(f"Closing connection to {addr} (Undeploying)")
            try:
                conn.close()
            except OSError as e:
                print(f"Error: socket.close() exception for {addr}: {e!r}")
            break
        message = serverLib.Message(conn, addr)
        message.read()
        # print("start writing")
        connected = message.write()


class Server:
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.socket = None
        self.threadList = []
        self.stop_threads = True
        self.deployed = False
        
       
    def __del__(self):
        self.undeploy()
        return
    def startListening(self):
        if not (self.socket is None) and self.deployed == True:
            return
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        print(f"Listening on {(self.host, self.port)}")
        self.deployed = True
        
        
        return
    def deploy(self,stopSig):
        self.startListening()
        self.stop_threads = False
        #print(len(self.read_list))
        read_list=[self.socket]
        while not (stopSig()):
            readable, writable, errored = select.select(read_list, [], [], 1)
            for s in readable:
                if s is self.socket:
                    conn, addr = self.socket.accept()
                    print(f"Accepted connection from {addr}")
                    thread = threading.Thread(target=handle_client, args=(conn, addr,(lambda : self.stop_threads)))
                    self.threadList.append(thread)
                    thread.daemon = True
                    thread.start()
                    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

                
    def undeploy(self):
        if self.deployed == True:
            self.stop_threads = True
            for item in self.threadList:
                item.join()
            del(self.threadList)
            self.threadList = []
            del(self.socket)
            self.socket = None
            self.deployed = False
            print("Undeploy complete")
            return

#server = Server(host,port)
#server.deploy()
        
        
        
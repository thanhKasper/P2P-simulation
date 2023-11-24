import sys
import json
import io
import struct
import tqdm
from pymongo import MongoClient
client = MongoClient("mongodb+srv://minhdangquocminh03:30S9qi0aPQZ5wSfO@clusterserver.xbnnkjh.mongodb.net/")
db = client.get_database('CN')
records = db.Client_Info

def SEND_request(client_name, path, filename):
    new_document = {
        "client_name" : client_name,
        "path" : path,
        "file_name": filename 
    }
    records.insert_one(new_document)
    return

def ADD_request_(address,filename,path):
    if records.count_documents({
            "client_name" : address,
            "file_name": filename
            }) > 0:
        return {"result": f"{filename} already exists."}
    else:
        SEND_request(address, path,filename)
        return {"result": f"{filename} added sucessfully."}

def REMOVE_request(clientname, filename):
    remove_query = {"$and":[
        {"file_name" : filename},
        {"client_name" : clientname}
        ]}
    records.delete_one(remove_query)
    return

def REMOVE_request_(address,filename):
    if records.count_documents({
            "client_name" : address,
            "file_name": filename
            }) == 0:
        return {"result": f"{filename} doesn't exist."}
    else:
        REMOVE_request(address, filename)
        return {"result": f"{filename} removed sucessfully."}

def UPDATE_request_(address,filename,path):
    if records.count_documents({
            "client_name" : address,
            "file_name": filename
            }) == 0:
        return {"result": f"{filename} doesn't exist."}
    else:
        UPDATE_request(address, path, filename)
        return {"result": f"{filename} updated sucessfully."}

def UPDATE_request(clientname, newpath, filename):
    update_query = {"$and":[
        {"file_name" : filename},
        {"client_name" : clientname}
        ]} 
    newvalues = {"$set" : {"path" : newpath}}
    records.update_one(update_query, newvalues)
    return

def FETCH_request(filename):
    if records.count_documents({
            "file_name": filename
            }) == 0:
        return {"result": f"{filename} doesn't exist."}
    else:
        data = {"client":[]}
        file_list = records.find({"file_name" : filename},{'_id':0})
        for file in file_list:
            data['client'].append(file)
        return data
    
def GET_request_(address):
    if records.count_documents({
            "client_name": address
            }) == 0:
        return {"result": "None"}
    else:
        data = {"client_info":[]}
        file_list = records.find({"client_name" : address},{'_id':0})
        for file in file_list:
            data['client_info'].append(file)
        return data

class Message:
    def __init__(self,socket,address):
        self.socket = socket
        self.address = address
        self._recv_buffer = b""
        self._send_buffer = b""
        self.json_header = None
        self.json_header_len = None
        self.request = None
        self.response_created = False
    def _read(self):
        try:
            # Should be ready to read
            data = self.socket.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")
    def _write(self):
        if self._send_buffer:
            print(f"Sending {self._send_buffer!r} to {self.address}")
            try:
                # Should be ready to write
                sent = self.socket.send(self._send_buffer)
                #print("DONE sending response")
            except BlockingIOError:
                #print("NOTDONE sending response")
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()
    def _json_encode(self , obj , encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)
    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes),encoding= encoding, newline = ""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj
    def process_fixedheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self.json_header_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]
    def process_jsonheader(self):
        hdrlen = self.json_header_len
        if len(self._recv_buffer) >= hdrlen:
            self.json_header = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ): 
                if reqhdr not in self.json_header:
                    raise ValueError(f"Missing required header '{reqhdr}' in JSON header.")
    def process_request(self):
        content_len = self.json_header["content-length"]
        if not len(self._recv_buffer) >= content_len:
            print("Content length of json message doesnt match")
            return
        data = self._recv_buffer[:content_len]            
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.json_header["content-type"] != "text/json":
            # Binary or unknown content-type
            self.request = data
            print(
                f"Received {self.json_header['content-type']} "
                f"request from {self.address}"
            )
            return
        encoding = self.json_header["content-encoding"]
        self.request = self._json_decode(data, encoding)
        print(f"Received request {self.request!r} from {self.address}")
    
    def read(self):
        self._read()
        
        if self.json_header_len is None:
            self.process_fixedheader()

        if self.json_header_len is not None:
            if self.json_header is None:
                self.process_jsonheader()
        
        if self.json_header:
            if self.request is None:
                self.process_request()
        #self.close()
    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()
        #print("done creating response")
        self._write()
    def _create_response_binary_content(self):
        response = {
            "content_bytes": b"First 10 bytes of request: "
            + self.request[:10],
            "content_type": "binary/custom-server-binary-type",
            "content_encoding": "binary",
        }
        return response
    def _create_response_json_content(self):
        content_encoding = "utf-8"
        if not 'action' in self.request.keys():
            content = {"result": "Error: invalid message (no action field)."}
        if self.request['action'] == 'SEND':
            content = ADD_request_(self.address,self.request['file_name'],self.request['path'])
        elif self.request['action'] == 'REMOVE':
            content = REMOVE_request_(self.address,self.request['file_name'])
        elif self.request['action'] == 'UPDATE':
            content = UPDATE_request_(self.address,self.request['file_name'],self.request['path'])
        elif self.request['action'] == 'FETCH':
            content = FETCH_request(self.request['file_name'])
        elif self.request['action'] == 'GET_INFO':
            content = GET_request_(self.address)
        else:
            content = {"result": f"Error: invalid action '{self.request['action']}'."}
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response
    def create_response(self):
        print("here0")
        if self.json_header["content-type"] == "text/json":
            response = self._create_response_json_content()
        else:
            response = self._create_response_binary_content()
        
        message = self._create_message(**response)
        
        self.response_created = True
        
        self._send_buffer += message
        
    def close(self):
        print(f"Closing connection to {self.address}")
        try:
            self.socket.close()
        except OSError as e:
            print(f"Error: socket.close() exception for {self.address}: {e!r}")
        finally:
            # Delete reference to socket object for garbage collection
            self.socket = None
    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message
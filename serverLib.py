import sys
import json
import io
import struct
import tqdm
from pymongo import MongoClient

client = MongoClient("mongodb+srv://minhdangquocminh03:30S9qi0aPQZ5wSfO@clusterserver.xbnnkjh.mongodb.net/")
db = client.get_database('CN')
records = db.Client_Info
onlineList = []


def CONNECT_request_(address, port, client_name,password):
    if records.count_documents({
        "client_name": client_name,
        "client_password": password
    }) > 0:
        onlineList.append(client_name)
        return {"result": f"Connected successfully."}
    if records.count_documents({
        "client_name": client_name
    }) > 0:
        return {"result": f"Wrong password."}
    else:
        records.insert_one({
            "client_name": client_name,
            "client_password": password,
            "IP": address,
            "port": port,
            "file_info": []
        })
        onlineList.append(client_name)
        return {"result": f"Welcome, {client_name}."}


def SEND_request(address, port, client_name, path, filename):
    records.update_one({"client_name": client_name}, {
        "$set": {
            "IP": address,
            "port": port
        },
        "$push": {
            "file_info": {
                "$each": [{"file_name": filename, "path": path}],
                "$sort": {"file_name": 1}
            }
        }
    })
    return


def ADD_request_(address, port, client_name, filename, path):
    if records.count_documents({
        "file_info.file_name": filename
    }) > 0:
        return {"result": f"{filename} already exists."}
    elif records.count_documents({
        "client_name": client_name,
        "file_info.file_name": filename
    }) > 0:
        return {"result": f"{filename} already exists."}
    else:
        SEND_request(address, port, client_name, path, filename)
        return {"result": f"{filename} added sucessfully."}


def REMOVE_request(address, port, client_name, filename):
    records.update_one({"client_name": client_name}, {
        "$set": {
            "IP": address,
            "port": port
        },
        "$pull": {
            "file_info": {
                "file_name": filename
            }
        }
    })
    return


def REMOVE_request_(address, port, clientname, filename):
    if records.count_documents({
        "client_name": clientname,
        "file_info.file_name": filename
    }) == 0:
        return {"result": f"{filename} doesn't exist."}
    else:
        REMOVE_request(address, port, clientname, filename)
        return {"result": f"{filename} removed sucessfully."}


def UPDATE_request_(address, port, client_name, filename, path):
    if records.count_documents({
        "client_name": client_name,
        "file_info.file_name": filename
    }) == 0:
        return {"result": f"{filename} doesn't exist."}
    else:
        UPDATE_request(address, port, client_name, filename, path)
        return {"result": f"{filename} updated sucessfully."}


def UPDATE_request(address, port, client_name, filename, path):
    records.update_one({"client_name": client_name, "file_info.file_name": filename}, {
        "$set": {
            "IP": address,
            "port": port,
            "file_info.$.path": path
        }
    })
    return


def FETCH_request(filename):
    if records.count_documents({
        "file_info.file_name": filename
    }) == 0:
        return {"result": f"{filename} doesn't exist in system."}
    else:
        data = {"client": []}
        count = 0
        file_list = records.find({"file_info.file_name": filename},
                                 {'_id': 0, "client_name": 1, "IP": 1,
                                  "file_info": {"$elemMatch": {"file_name": filename}}})
        # "file_name": "$file_info.file_name"})
        for file in file_list:
            if file['client_name'] in onlineList:
                result = dict(client_name=file['client_name'], IP=file['IP'], path=file["file_info"][0]['path'])
                data['client'].append(result)
                count = count + 1
        data["result"] = f"There are {count} clients online having {filename}."
        return data


def GET_request_(client_name, address, port):
    if records.count_documents({
        "client_name": client_name
    }) == 0:
        return {"result": "None"}
    else:
        records.update_one({"client_name": client_name}, {
            "$set": {
                "IP": address,
                "port": port
            }
        })
        data = {"result": "Retrieve client information sucessfully", "client": []}
        file_list = records.find({"client_name": client_name},
                                 {'_id': 0, "IP": 1, "client_name": 1, "port": 1, "file_info": 1})
        for file in file_list:
            data['client'].append(file)
        return data


class Message:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self._recv_buffer = b""
        self._send_buffer = b""
        self.json_header = None
        self.json_header_len = None
        self.request = None
        self.response_created = False
        # self.lock = lock

    def __del__(self):
        self.socket = None
        # print("message Done")
        return

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
                # print("DONE sending response")
            except BlockingIOError:
                # print("NOTDONE sending response")
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    if self.request["action"] == "LEAVE":
                        self.close()
                        return False
                        # self.__del__()
        return True

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        obj = json.loads(json_bytes.decode(encoding))
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
            # print(
            # f"Received {self.json_header['content-type']}"
            # f"request from {self.request['client_name']}, {self.address}"
            # )
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
        # self.close()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()
        # print("done creating response")
        flag = self._write()
        return flag

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
            content = ADD_request_(self.address[0], self.address[1], self.request['client_name'],
                                   self.request['file_name'], self.request['path'])
        elif self.request['action'] == 'LEAVE':
            onlineList.remove(self.request['client_name'])
            content = {"result": "CLOSING"}
        elif self.request['action'] == 'CONNECT':
            content = CONNECT_request_(self.address[0], self.address[1], self.request['client_name'],self.request['client_password'])
        elif self.request['action'] == 'REMOVE':
            content = REMOVE_request_(self.address[0], self.address[1], self.request['client_name'],
                                      self.request['file_name'])
        elif self.request['action'] == 'UPDATE':
            content = UPDATE_request_(self.address[0], self.address[1], self.request['client_name'],
                                      self.request['file_name'], self.request['path'])
        elif self.request['action'] == 'FETCH':
            content = FETCH_request(self.request['file_name'])
        elif self.request['action'] == 'GET_INFO':
            content = GET_request_(self.request['client_name'], self.address[0], self.address[1])
        else:
            content = {"result": f"Error: invalid action '{self.request['action']}'."}
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response

    def create_response(self):

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

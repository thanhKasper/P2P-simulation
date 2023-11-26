import sys
import json
import io
import struct

class Message:
    def __init__(self,socket,address,request):
        
        self.socket = socket
        self.address = address
        self.request = request
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self.json_header_len = None
        self.json_header = None
        self.response = None
    def __del__(self):
        self.socket = None
        #print("message Done")
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
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
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
    
    def read(self):
        self._read()
        
        if self.json_header_len is None:

            self.process_fixedheader()

        if self.json_header_len is not None:
            if self.json_header is None:
                self.process_jsonheader()
        
        if self.json_header:
            if self.response is None:
                self.process_response()
                

    def write(self):
        if not self._request_queued:
            self.queue_request()
        self._write()
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
    def queue_request(self):
        content = self.request["content"]
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]
        if content_type == "text/json":
            req = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        else:
            req = {
                "content_bytes": content,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        message = self._create_message(**req)
        self._send_buffer += message
        self._request_queued = True
    
    def process_response(self):
        content_len = self.json_header["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.json_header["content-type"] == "text/json":
            encoding = self.json_header["content-encoding"]
            self.response = self._json_decode(data, encoding)
            #print(f"Received response {self.response!r} from {self.address}")
            self._process_response_json_content()
        else:
            # Binary or unknown content-type
            self.response = data
            print(
                f"Received {self.json_header['content-type']} "
                f"response from {self.addr}"
            )
            self._process_response_binary_content()
        # Close when response has been processed
        #self.__del__()
        #self.close()
        
    def _process_response_json_content(self):
        content = self.response
        result = content.get("result")
        print(f"Got result: {result}")

    def _process_response_binary_content(self):
        content = self.response
        print(f"Got response: {content!r}")
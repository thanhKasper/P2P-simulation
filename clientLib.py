import sys
import json
import io
import struct

'''
The Structure of the Protocol

++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++
++          header length (2 bytes)         ++
++++++++++++++++++++++++++++++++++++++++++++++
++  byte order: big endian / little endian  ++
++  content-length: size of payload         ++
++  content-type: text/json                 ++
++  content-encoding: utf-8/ascii           ++
++++++++++++++++++++++++++++++++++++++++++++++
++                 Payload                  ++
++++++++++++++++++++++++++++++++++++++++++++++

'''


class Message:
    def __init__(self, socket, address, request):
        self.socket = socket
        self.address = address
        self.request = request  # Python string/dict that need to convert to bytestream data to send to the Internet
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self.json_header_len = None
        self.json_header = None
        self.response = None  # Output data after receiving the bytestream data from the Internet

    def __del__(self):
        self.socket = None
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

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        obj = json.loads(json_bytes.decode(encoding))
        return obj

    # Retrieve the size in byte of the header (json_header)
    def process_fixedheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self.json_header_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    # Extract the json_header as well as the payload
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
                return self.process_response()
        return None

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

    # Combine the header and payload together to create a message packet
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

    # Turning a Python syntax into a bytestream data
    def queue_request(self):
        content = self.request["content"]  # Python syntax for payload
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]
        # The payload is the json file
        if content_type == "text/json":
            req = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        # The payload is a normal string
        else:
            req = {
                "content_bytes": content,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        message = self._create_message(**req)
        self._send_buffer += message
        self._request_queued = True

    # Converting a bytestream data into python workable syntax
    def process_response(self):
        content_len = self.json_header["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return None
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.json_header["content-type"] == "text/json":
            encoding = self.json_header["content-encoding"]
            self.response = self._json_decode(data, encoding)
            # print(f"Received response {self.response!r} from {self.address}")
            return self._process_response_json_content()
        else:
            # Binary or unknown content-type
            self.response = data
            print(
                f"Received {self.json_header['content-type']} "
                f"response from {self.addr}"
            )
            self._process_response_binary_content()
            return None
    def _process_response_json_content(self):
        content = self.response
        result = content.get("result")
        print(f"Got result: {result}")
        if 'client' in content:
            return content.get("client")
        return None

    def _process_response_binary_content(self):
        content = self.response
        print(f"Got response: {content!r}")

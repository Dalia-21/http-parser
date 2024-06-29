import socket
from request_parser import RequestParser


class Server:

    chunk_length = 1024
    telnet_termination_code = b'\xff\xf4\xff\xfd\x06'
    
    def __init__(self, port=8000):
        self.port = port
        self.address: tuple = ('127.0.0.1', port)
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Program displays output synchronously, so queued requests are not needed
        self.connection_limit = 0

        self.parser: RequestParser = RequestParser()


    def start(self):
        self.socket.bind(self.address)
        self.socket.listen(self.connection_limit)
        print(f"Listening on port {self.port} ...")


    def accept_request(self) -> str:
        (client_socket, client_address) = self.socket.accept()
        print(f"Accepted connection from {client_address}")
        
        while (chunk := client_socket.recv(Server.chunk_length)) != b'':
            if chunk == Server.telnet_termination_code:
                client_socket.close()
                # Simpler than raising an exception, though arguably a bit of a hack
                return "Connection was terminated by client"

            print(f"Received data: {chunk}")
            self.parser.add_chunk(chunk)
            if self.parser.end_transmission():
                break
        
        response = b"HTTP/1.1 204 NO-CONTENT\r\n\r\n"
        client_socket.send(response)
        client_socket.close()
        print("Connection closed")

        parsed_string = self.parser.request_to_string()
        return parsed_string

    def close(self):
        print("\nShutting down server now.")
        self.socket.close()


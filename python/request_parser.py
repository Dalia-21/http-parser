class RequestParser:

    def __init__(self):
        self.request_lines: list[str] = ""
        self.request_method: str = ""
        self.path: str = ""
        self.http_version: str = ""
        self.headers: dict[str, str] = {}
        self.request_body: str = ""
        self.request_line_complete: bool = False
        self.headers_complete: bool = False
        self.end_of_headers_received: bool = False
        self.headers_received: bool = False
        self.request_line_in_chunk: bool = False

    def reset(self):
        self.request_method = self.path \
        = self.http_version = self.request_body = ""
        self.request_lines = []
        self.headers = {}
        self.request_line_complete = self.headers_complete = \
        self.end_of_headers_received = self.headers_received = \
        self.request_line_in_chunk = False

    def add_chunk(self, chunk: bytes) -> None:
        self.parse_request(chunk)

    def end_transmission(self) -> bool:
        if self.request_method == "GET" and self.end_of_headers_received:
            return True
        elif self.request_method == "POST":
            return self.content_limit_reached()
        else:
            return False  # Other methods not supported for simplicity

    def content_limit_reached(self) -> bool:
        return len(self.request_body) >= int(self.headers["Content-Length"])

    def parse_request(self, chunk: bytes) -> None:
        if b'\r\n\r\n' in chunk or chunk == b'\r\n':
            self.end_of_headers_received = True
        self.headers_received = b': ' in chunk
        self.lines = list(map(lambda x: x.decode(), chunk.split(b'\r\n')))
        
        if not self.request_line_complete:
            self.parse_request_line()
        else:
            self.request_line_in_chunk = False
        
        end_headers_index = 0
        if not self.headers_complete:
            end_headers_index = self.parse_headers()
        
        if self.headers_complete:
            self.parse_body(end_headers_index)

    def parse_request_line(self):
        self.request_method, self.path, self.http_version = self.lines[0].split()
        self.request_line_complete = True
        self.request_line_in_chunk = True

    def parse_headers(self) -> int:
        if not self.headers_received:
            return -1
        for idx, line in enumerate(self.lines[1 if self.request_line_in_chunk else 0:]):
            if ":" not in line and self.end_of_headers_received:
                self.headers_complete = True
                return idx + 1  # +1 to account for request line
            if line:
                header_line = line.split(": ")
                self.headers[header_line[0]] = header_line[1]
        return -1  # Chunk ended before headers finished

    def parse_body(self, end_headers_index: int):
        self.request_body += "".join(self.lines[end_headers_index:])

    def request_to_string(self) -> str:
        request_string = \
"""
> Request Method: {method}
> Request Path:   {path}
> HTTP Version:   {version}

> HEADERS:
{headers}
> Request Body:
{body}
""".format(
            method=self.request_method,
            path=self.path,
            version=self.http_version,
            headers=self.headers_to_string(),
            body=self.request_body
        )
        return request_string

    def headers_to_string(self):
        headers_string = ""
        for key, value in self.headers.items():
            headers_string += f"> {key}: {value}\n"
        headers_string += "\n"
        return headers_string


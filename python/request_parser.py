import re


class ParsingException(Exception):
    pass


class RequestParser:

    def __init__(self):
        self.lines: list[str] = ""
        self.request_method: str = ""
        self.path: str = ""
        self.http_version: str = ""
        self.queries: dict[str, str] = {}
        self.headers: dict[str, str] = {}
        self.request_body: str = ""
        self.request_line_complete: bool = False
        self.headers_complete: bool = False
        self.end_of_headers_received: bool = False

    def reset(self):
        self.request_method = self.path \
        = self.http_version = self.request_body = ""
        self.lines = []
        self.queries = {}
        self.headers = {}
        self.request_line_complete = self.headers_complete = self.end_of_headers_received = False

    def add_chunk(self, chunk: bytes) -> None:
        self.parse_request(chunk)
        try:
            self.validate_request()
        except ParsingException as e:
            self.reset()
            raise e

    def validate_request(self):
        if self.request_line_complete:
            self.validate_request_line()
        if self.headers_complete:
            self.validate_headers()
            if self.request_method in ["POST", "PATCH", "PUT", "DELETE"] and "Content-Length" in self.headers:
                self.validate_request_body()

    def validate_request_line(self) -> None:
        if self.request_method.upper() not in ["GET", "POST", "PATCH", "PUT", "DELETE"]:
            raise ParsingException(f"Unknown request method {self.request_method}")
        http_version_expression = r'HTTP/[0-9]\.[0-9]'
        if not re.search(http_version_expression, self.http_version):
            raise ParsingException(f"Invalid HTTP version {self.http_version}")
        if not self.path.startswith("/"):  # More complicated path matching is out of scope
            raise ParsingException(f"Request path must start with /: {self.path}")

    def validate_headers(self):
        if self.request_method == "GET" and "Content-Length" in self.headers:
            raise ParsingException("Content-Length header should not be present in GET request")
        if self.request_method in ["POST", "PUT", "PATCH"] and "Content-Length" not in self.headers:
            raise ParsingException("Content-Length header must be present for requests which expect a body")

    def validate_request_body(self):
        if len(self.request_body) > int(self.headers["Content-Length"]):
            raise ParsingException(f"Body length: {len(self.request_body)} exceeds stated Content-Length: {int(self.headers["Content-Length"])}")

    def end_transmission(self) -> bool:
        if self.request_method.upper() == "GET":
            return self.end_of_headers_received
        elif self.request_method.upper() in ["POST", "PATCH", "PUT"]:
            return self.content_limit_reached()
        elif self.request_method.upper() == "DELETE":
            if "Content-Length" in self.headers:
                return self.content_limit_reached()
            else:
                return self.end_of_headers_received
        else:
            return False

    def content_limit_reached(self) -> bool:
        return "Content-Length" in self.headers \
        and len(self.request_body) >= int(self.headers["Content-Length"])

    def parse_request(self, chunk: str) -> None:
        self.lines = chunk.split("\r\n")
        
        offset = 1 if not self.request_line_complete else 0
        if not self.request_line_complete:
            self.parse_request_line()
        
        if "\r\n\r\n" in chunk or chunk == "\r\n":
            self.end_of_headers_received = True
            if len(self.lines) == 2:
                self.headers_complete = True
        if ":" in chunk and not self.headers_complete:
            offset = self.parse_headers(offset)
        
        if self.end_of_headers_received:
            self.parse_body(offset)

    def parse_request_line(self):
        self.request_method, self.path, self.http_version = self.lines[0].split()
        self.parse_queries()
        self.request_line_complete = True

    def parse_queries(self):
        if "?" in self.path:
            self.path, query_text = self.path.split("?")
            query_entries = query_text.split("&")
            for entry in query_entries:
                entry_line = entry.split("=")
                self.queries[entry_line[0]] = entry_line[1]

    def parse_headers(self, offset: int) -> int:
        for idx, line in enumerate(self.lines[offset:]):
            if RequestParser.is_valid_header_line(line):
                key, value = line.split(":", 1)
                self.headers[key] = value.strip()
            else:
                if self.end_of_headers_received:
                    self.headers_complete = True
                    return idx + offset
        return 0  # Chunk ended before headers finished

    @staticmethod
    def is_valid_header_line(line: str) -> bool:
        return bool(line) and ":" in line and not line.isspace()

    def parse_body(self, end_headers_index: int):
        self.request_body += "".join(list(filter(lambda x: not x.isspace(), self.lines[end_headers_index:])))

    def request_to_string(self) -> str:
        request_string = \
"""
> Request Method: {method}
> Request Path:   {path}
> Queries:
{queries}
> HTTP Version:   {version}

> HEADERS:
{headers}
> Request Body:
{body}
""".format(
            method=self.request_method,
            path=self.path,
            queries=self.queries_to_string(),
            version=self.http_version,
            headers=self.headers_to_string(),
            body=self.request_body
        )
        self.reset()
        return request_string

    def queries_to_string(self):
        queries_string = ""
        for key, value in self.queries.items():
            queries_string += f"> {key}: {value}\n"
        return queries_string

    def headers_to_string(self):
        headers_string = ""
        for key, value in self.headers.items():
            headers_string += f"> {key}: {value}\n"
        headers_string += "\n"
        return headers_string


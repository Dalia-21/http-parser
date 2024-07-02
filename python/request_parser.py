import re


class ParsingException(Exception):
    pass


class RequestParser:

    def __init__(self):
        self.request_method: str = ""
        self.path: str = ""
        self.http_version: str = ""
        self.queries: dict[str, str] = {}
        self.headers: dict[str, str] = {}
        self.request_body: str = ""
        self.request_line_complete: bool = False
        self.headers_complete: bool = False

    def reset(self):
        self.request_method = self.path \
        = self.http_version = self.request_body = ""
        self.queries = {}
        self.headers = {}
        self.request_line_complete = self.headers_complete = False

    def add_chunk(self, chunk: str) -> None:
        try:
            self.parse_request(chunk)
            self.validate_request()
        except ParsingException as e:
            self.reset()
            raise e

    def parse_request(self, chunk: str):
        if RequestParser.whole_request_sent(chunk):
            self.parse_whole_request(chunk)
        else:
            self.parse_line(chunk)

    @staticmethod
    def whole_request_sent(chunk: str) -> bool:
        """A single line GET request will still end in a double carriage return, line feed.
        A single line sent by telnet during an ongoing request will only have one carriage return and line feed."""
        return "\r\n\r\n" in chunk

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
        for key in self.headers:
            if not re.match(r'^[A-Za-z-]+$', key):
                raise ParsingException(f"Invalid header key: {key} - keys must be only letters and dashes")
        if self.request_method == "GET" and "Content-Length" in self.headers:
            raise ParsingException("Content-Length header should not be present in GET request")
        if self.request_method in ["POST", "PUT", "PATCH"] and "Content-Length" not in self.headers:
            raise ParsingException("Content-Length header must be present for requests which expect a body")

    def validate_request_body(self):
        if len(self.request_body) > int(self.headers["Content-Length"]):
            raise ParsingException(
                f"Body length: {len(self.request_body)} exceeds stated Content-Length: {int(self.headers["Content-Length"])}")

    def end_transmission(self) -> bool:
        if self.request_method.upper() == "GET":
            return self.headers_complete
        elif self.request_method.upper() in ["POST", "PATCH", "PUT"]:
            return self.content_limit_reached()
        elif self.request_method.upper() == "DELETE":
            if "Content-Length" in self.headers:
                return self.content_limit_reached()
            else:
                return self.headers_complete
        else:
            return False

    def content_limit_reached(self) -> bool:
        return "Content-Length" in self.headers \
        and len(self.request_body) >= int(self.headers["Content-Length"])



    def parse_line(self, chunk: str) -> None:
        line = chunk.removesuffix("\r\n")

        if not self.request_line_complete:
            self.parse_request_line(line)
            self.request_line_complete = True
        elif not self.headers_complete:
            if not line:
                self.headers_complete = True
            else:
                self.parse_header(line)
        else:
            self.parse_body_line(line)
        
    def parse_whole_request(self, chunk: str) -> None:
        request_line_and_headers, body = chunk.split("\r\n\r\n", 1)
        request_line_and_headers = request_line_and_headers.split("\r\n")
        self.parse_request_line(request_line_and_headers[0])
        for header in request_line_and_headers[1:]:
            self.parse_header(header)
        self.headers_complete = True
        for line in body.split("\r\n"):
            self.parse_body_line(line)

    def parse_request_line(self, request_line: str):
        split_line = request_line.split(" ", 3)
        if len(split_line) != 3:
            raise ParsingException(f"Request line must contain method, path and verson: {request_line}")
        self.request_method, self.path, self.http_version = split_line
        self.request_method = self.request_method.upper()
        self.parse_queries()
        self.request_line_complete = True

    def parse_queries(self):
        if "?" not in self.path:
            return
        self.path, query_text = self.path.split("?", 1)
        query_entries = query_text.split("&")
        for entry in query_entries:
            entry_line = entry.split("=")
            self.queries[entry_line[0]] = entry_line[1]

    def parse_header(self, header_line: str) -> None:
        """Header key is converted to title case, as this seems to be standard
        for HTTP headers. Value is stripped of whitespace, since this is not meaningful.
        Multiple colons are not expected in header values, but only one split is allowed
        to prevent errors."""
        if ":" not in header_line:
            raise ParsingException(f"Invalid header line provided: {line}")
        key, value = header_line.split(":", 1)
        self.headers[key.title()] = value.strip()

    def parse_body_line(self, line: str):
        self.request_body += line

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
            queries_string += f"> {key:<{RequestParser.longest_line(self.queries.keys())}}: {value}\n"
        return queries_string

    def headers_to_string(self):
        headers_string = ""
        for key, value in self.headers.items():
            headers_string += f"> {key:<{RequestParser.longest_line(self.headers.keys())}}: {value}\n"
        return headers_string

    @staticmethod
    def longest_line(keys: list) -> int:
        return max(map( lambda x: len(x), keys))


import pytest
from request_parser import RequestParser

class TestParserParsing:
    parser = RequestParser()

    @pytest.fixture(autouse=True)
    def before_each(self):
        self.parser.reset()

    def test_parse_request_line_simple(self):
        http_request = "GET / HTTP/1.1"
        self.parser.parse_request_line(http_request)

        assert self.parser.request_method == "GET"
        assert self.parser.http_version == "HTTP/1.1"
        assert self.parser.path == "/"

    def test_parse_request_line_with_queries(self):
        http_request = "GET /search?q=test&count=3 HTTP/1.1"
        self.parser.parse_request_line(http_request)

        assert self.parser.path == "/search"
        assert "q" in self.parser.queries and self.parser.queries["q"] == "test"
        assert "count" in self.parser.queries and self.parser.queries["count"] == "3"

    def test_parse_headers(self):
        request_line = "POST / HTTP/1.1"

        user_agent_header = "User-Agent: telnet"
        content_type_header = "Content-Type: application/json"
        accept_header = "Accept: */*"
        content_length_header = "Content-Length: 20"

        empty_line = ""
        request_body = "{'data': 'value'}"

        for line in [
            request_line,
            user_agent_header,
            content_type_header,
            accept_header,
            content_length_header,
            empty_line,
            request_body
        ]:
            self.parser.parse_request(line)
        self.parser.headers_complete = True

        assert len(self.parser.headers) == 4

    def test_parse_headers_single_lines(self):
        user_agent_header = "User-Agent: telnet\r\n"
        content_type_header = "Content-Type: application/json\r\n"
        accept_header = "Accept: */*\r\n"
        content_length_header = "Content-Length: 20\r\n"

        for line in [
            user_agent_header,
            content_type_header,
            content_length_header,
            accept_header
        ]:
            self.parser.parse_header(line)

        self.parser.headers_complete = True

        assert len(self.parser.headers) == 4

    def test_parse_body(self):
        request_body = "{'data': 'value'}"

        self.parser.parse_body_line(request_body)

        assert self.parser.request_body == request_body

    def test_parse_request_whole_GET_request(self):
        chunk = b'''GET / HTTP/1.1\r\nHost: localhost\r\nAccept: */*\r\nUser-Agent: curl\r\n\r\n'''

        self.parser.parse_request(chunk.decode())

        assert self.parser.request_method == "GET"
        assert self.parser.path == "/"
        assert not self.parser.queries
        assert self.parser.http_version == "HTTP/1.1"
        assert self.parser.request_line_complete == True

        assert len(self.parser.headers) == 3
        assert self.parser.headers_complete == True

        assert not self.parser.request_body

    def test_parse_request_whole_POST_request(self):
        chunk = b'''POST / HTTP/1.1\r\nContent-Type: application/json\r\nContent-Length: 17\r\nUser-Agent: curl\r\nAccept: */*\r\n\r\n{\'data\': \'value\'}\r\n'''

        self.parser.parse_request(chunk.decode())

        assert self.parser.request_method == "POST"
        assert self.parser.path == "/"
        assert self.parser.http_version == "HTTP/1.1"
        assert not self.parser.queries
        assert self.parser.request_line_complete == True

        assert len(self.parser.headers) == 4
        assert self.parser.headers_complete == True

        assert self.parser.request_body == "{'data': 'value'}"

    def test_parse_request_GET_single_lines(self):
        request_line = b'GET / HTTP/1.1\r\n'
        user_agent_header = b'User-Agent: telnet\r\n'
        accept_header = b'Accept: */*\r\n'
        host_header = b'Host: localhost\r\n'
        empty_line = b'\r\n'

        for line in [
            request_line,
            user_agent_header,
            accept_header,
            host_header,
            empty_line
        ]:
            self.parser.parse_request(line.decode())

        assert self.parser.request_method == "GET"
        assert self.parser.http_version == "HTTP/1.1"
        assert self.parser.path == "/"
        assert self.parser.request_line_complete == True

        assert len(self.parser.headers) == 3
        assert self.parser.headers_complete == True

        assert not self.parser.request_body

    def test_parse_request_POST_single_lines(self):
        request_line = b'POST / HTTP/1.1\r\n'
        user_agent_header = b'User-Agent: telnet\r\n'
        accept_header = b'Accept: */*\r\n'
        host_header = b'Host: localhost\r\n'
        content_type_header = b'Content-Type: application/json\r\n'
        content_length_header = b'Content-Length: 17\r\n'
        empty_line = b'\r\n'
        request_body = b'{\'data\': \'value\'}\r\n'
        
        for line in [
            request_line,
            user_agent_header,
            accept_header,
            host_header,
            content_type_header,
            content_length_header,
            empty_line,
            request_body,
            empty_line
        ]:
            self.parser.parse_request(line.decode())

        assert self.parser.request_method == "POST"
        assert self.parser.path == "/"
        assert self.parser.http_version == "HTTP/1.1"
        assert self.parser.request_line_complete == True

        assert len(self.parser.headers) == 5
        assert self.parser.headers_complete == True

        assert self.parser.request_body == "{'data': 'value'}"


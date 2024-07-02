import pytest
from request_parser import RequestParser, ParsingException


class TestParserValidation:
    parser = RequestParser()

    @pytest.fixture(autouse=True)
    def before_each(self):
        self.parser.reset()

    def test_parse_request_line(self):
        invalid_request_line = "GET /path"
        with pytest.raises(ParsingException):
            self.parser.parse_request_line(invalid_request_line)

    def test_validate_request_line_invalid_method(self):
        self.parser.request_method = "INVALID_METHOD"
        with pytest.raises(ParsingException):
            self.parser.validate_request_line()

    def test_validate_request_line_invalid_version(self):
        self.parser.request_method = "GET"
        self.parser.http_version = "HTTP/d.d"
        with pytest.raises(ParsingException):
            self.parser.validate_request_line()

    def test_validate_request_line_invalid_path(self):
        self.parser.request_method = "GET"
        self.parser.http_version = "HTTP/1.1"
        self.parser.path = "invalid/path"
        with pytest.raises(ParsingException):
            self.parser.validate_request_line()

    def test_validate_headers_invalid_key(self):
        self.parser.headers = {"@#$": "invalid_key_characters"}
        with pytest.raises(ParsingException):
            self.parser.validate_headers()

    def test_validate_headers_GET_with_content_length(self):
        self.parser.request_method = "GET"
        self.parser.headers = {"Content-Length": "20"}
        with pytest.raises(ParsingException):
            self.parser.validate_headers()

    def test_validate_headers_POST_without_content_length(self):
        self.parser.request_method = "POST"
        self.parser.headers = {}
        with pytest.raises(ParsingException):
            self.parser.validate_headers()

    def test_validate_body_exceeds_content_length(self):
        self.parser.headers = {"Content-Length": "10"}
        self.parser.request_body = "*" * 20
        with pytest.raises(ParsingException):
            self.parser.validate_request_body()


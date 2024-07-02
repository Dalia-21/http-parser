import pytest
from request_parser import RequestParser


class TestParserHTTPMethods:
    parser = RequestParser()

    @pytest.fixture(autouse=True)
    def before_each(self):
        self.parser.reset()

    def test_end_transmission_GET_should_return_true(self):
        self.parser.request_method = "GET"
        self.parser.headers_complete = True

        assert self.parser.end_transmission()

    def test_end_transmission_GET_should_return_false(self):
        self.parser.request_method = "GET"
        
        assert not self.parser.end_transmission()

    def test_end_transmission_POST_should_return_true(self):
        content_length = 10
        self.parser.request_method = "POST"
        self.parser.headers = {"Content-Length": content_length}
        self.parser.request_body = "*" * content_length

        assert self.parser.end_transmission()

    def test_end_transmission_POST_should_return_false(self):
        content_length = 10
        self.parser.request_method = "POST"
        self.parser.headers = {"Content-Length": content_length}
        self.parser.end_of_headers_received = True  # Misdirection
        self.parser.request_body = ""

        assert not self.parser.end_transmission()


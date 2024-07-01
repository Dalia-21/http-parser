from request_parser import RequestParser

class TestParserRest:
    parser = RequestParser()
    
    def test_reset(self):
        self.parser.lines = ["Non", "empty", "list"]
        self.parser.request_method = self.parser.path = \
        self.parser.http_version = self.parser.request_body = "Non empty string"
        self.parser.queries = self.parser.headers = {"Dict": "with", "some": "contents"}
        self.parser.request_line_complete = self.parser.end_of_headers_received = True

        self.parser.reset()

        assert self.parser.request_method == self.parser.path == \
            self.parser.http_version == self.parser.request_body == ""
        assert self.parser.lines == []
        assert self.parser.queries == self.parser.headers == {}
        assert self.parser.request_line_complete == self.parser.end_of_headers_received == False


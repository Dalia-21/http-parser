#include <string>
#include <map>
#include <set>
#include <format>

#include "parser.h"
#include "parsing_exception.h"

static const std::set<std::string> http_methods{ "GET", "POST", "PUT", "PATCH", "DELETE" };
static const std::set<std::string> body_required_methods{ "POST", "PUT", "PATCH" };

static bool isValidHeaderLine(std::string line) {
  return line.find(':') != std::string::npos;
}

Parser::Parser() {
};

void Parser::addChunk(std::string chunk) {
  parseRequest(chunk);
  try {
    validateRequest();
  } catch (ParsingException e) {
    reset();
    throw e;
  }
}

void Parser::reset() {
  m_chunk = m_method = m_path = m_version = m_body = "";
  m_request_line_complete = m_headers_complete = m_end_of_headers_received = false;
  m_queries.clear();
  m_headers.clear();
}

bool Parser::transmissionEnded() {
  if (m_method.compare("GET") == 0) {
    return m_headers_complete;
  } else if (body_required_methods.find(m_method) != body_required_methods.end()) {
    return contentLimitReached();
  } else if (m_method.compare("DELETE") == 0) { // MAKE SURE METHODS ARE UPPERCASED ON INITIALIZATION
    if (m_headers.find("Content-Length") != m_headers.end()) {
      return contentLimitReached();
    } else {
      return m_headers_complete;
    }
  } else { // Unreachable
    return false;
  }
}

bool Parser::contentLimitReached() {
  return m_headers.find("Content-Length") != m_headers.end() &&
    std::stoi(m_headers.find("Content-Length")->second) == m_body.length(); // ADD VALIDATION THAT THIS IS INT
}

void Parser::validateRequest() {
  if (m_request_line_complete) {
    validateRequestLine();
  }
  if (m_headers_complete) {
    validateHeaders();
    if (m_method.compare("GET") != 0 && m_headers.find("Content-Length") != m_headers.end()) {
      validateBody();
    }
  }
}

void Parser::validateRequestLine() {
  if (http_methods.find(m_method) == http_methods.end()) {
    throw ParsingException(std::format("Unknown request method {}", m_method));
  }
  // HTTP version regex
  if (m_path.rfind("/", 0) != 0) {
    throw ParsingException(std::format("Request path must start with /: {}", m_path));
  }
}

void Parser::validateHeaders() {
  if (m_method.compare("GET") == 0 && m_headers.find("Content-Length") != m_headers.end()) {
    throw ParsingException("Content-Length header should not be present in GET request");
  } else if (body_required_methods.find(m_method) != body_required_methods.end()
      && m_headers.find("Content-Length") == m_headers.end()) {
    throw ParsingException("Content-Length must be present for requests which require a body");
  }
}

void Parser::validateBody() {
  if (m_body.length() > std::stoi(m_headers.at("Content-Length"))) {
    throw ParsingException(std::format("Body length: {} exceeds stated Content-Length: {}",
          m_body.length(), m_headers.at("Content-Length")));
  }
}

void Parser::parseRequest(std::string chunk) {

}

void Parser::parseRequestLine() {}
void Parser::parseQueries() {}
int Parser::parseHeaders() {
  return 0;
}
void Parser::parseBody() {}

std::string Parser::requestToString() {
  return "";
}

std::string Parser::headersToString() {
  return "";
}

std::string Parser::queriesToString() {
  return "";
}


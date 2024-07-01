#ifndef PARSER_H
#define PARSER_H

#include <string>
#include <map>

class Parser {
  private:
    std::string m_chunk;
    std::string m_method;
    std::string m_path;
    std::string m_version;
    std::map<std::string, std::string> m_queries;
    std::map<std::string, std::string> m_headers;
    std::string m_body;
    bool m_request_line_complete;
    bool m_headers_complete;
    bool m_end_of_headers_received;

    void reset();
    bool contentLimitReached();


    void validateRequest();
    void validateRequestLine();
    void validateHeaders();
    void validateBody();

    void parseRequest(std::string chunk);
    void parseRequestLine();
    void parseQueries();
    int parseHeaders();
    void parseBody();

    std::string headersToString();
    std::string queriesToString();

  public:
    Parser();

    void addChunk(std::string chunk);
    bool transmissionEnded();
    std::string requestToString();
};

#endif

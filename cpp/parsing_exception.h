#ifndef PARSING_EXCEPTION_H
#define PARSING_EXCEPTION_H

#include <string>

class ParsingException {
  private:
    std::string m_error;

  public:
    ParsingException(std::string error);
    std::string getError();
};

#endif

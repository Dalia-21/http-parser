#include <string>

#include "parsing_exception.h"

ParsingException::ParsingException(std::string error)
  : m_error{ error }
{
}

std::string ParsingException::getError() {
  return m_error;
}

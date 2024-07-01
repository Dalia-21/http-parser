#include <iostream>
#include <stdlib.h>
#include <sys/socket.h>

#include "server.h"
#include "connection.h"
#include "parsing_exception.h"
#include "parser.h"

Server::Server(std::string port)
  : m_port{ port }
  , m_connection { Connection(m_port, 1, 1024) }
{
}

void Server::start() {
  m_connection.start();
}

std::string Server::process_request() {
  m_connection.accept_connection();
  std::string processed_request = "Running the process_request member function now.\n";
  // while chunks received not done
  // std::string received string += m_connection.receive_string();

  std::string termination_response = "HTTP/1.1 204 NO-CONTENT\r\n\r\n";

  m_connection.close_connection(termination_response);
  return processed_request;
}

void Server::close() {
  m_connection.close_socket();
  std::cout << "Shutting down server now.\n";
}


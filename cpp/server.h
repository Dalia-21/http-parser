#ifndef SERVER_H
#define SERVER_H

#include <iostream>
#include <sys/socket.h>

#include "connection.h"

class Server {
  private:
    std::string m_port;
    int m_sockfd, m_clientfd;
    Connection m_connection;
    // Parser

  public:
    Server(std::string port);

    void start();
    std::string process_request();
    void close();
};

#endif


#ifndef CONNECTION_H
#define CONNECTION_H

#include <iostream>
#include <stdlib.h>
#include <sys/socket.h>

class Connection {
  private:
    int m_connection_limit;
    int m_receive_char_limit;
    std::string m_port;
    int m_sockfd, m_clientfd;
    struct sockaddr_storage m_client_addr;
    
  public:
    Connection(std::string port, int connection_limit, int receive_char_limit);

    void start();
    void accept_connection();
    std::string receive_string();
    void send_string(std::string response);
    void close_connection(std::string response);
    void close_socket();
};

#endif


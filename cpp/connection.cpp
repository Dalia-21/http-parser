#include <iostream>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>

#include "connection.h"

Connection::Connection(std::string port, int connection_limit, int receive_char_limit)
  : m_port{ port }
  , m_connection_limit{ connection_limit }
  , m_receive_char_limit{ receive_char_limit }
  , m_sockfd{ 0 }
  , m_clientfd{ 0 }
  , m_client_addr{ }
{

}

void Connection::start() {
  struct addrinfo config, *servinfo, *next;
  memset(&config, 0, sizeof config);
  config.ai_family = AF_INET;
  config.ai_socktype = SOCK_STREAM;
  config.ai_flags = AI_PASSIVE;

  int rv;
  if ((rv = getaddrinfo(NULL, m_port.c_str(), &config, &servinfo)) != 0) {
    std::cerr << "Failed to get local address info: " << gai_strerror(rv) << "\n";
    // Handle exiting with error
  }

  for (next = servinfo; next != NULL; next = next->ai_next) {
    if ((m_sockfd = socket(next->ai_family, next->ai_socktype,
            next->ai_protocol)) == -1) {
      perror("server: socket"); // Work out c++ error handling here
      continue;
    }

    int yes = 1;
    if (setsockopt(m_sockfd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int))) {
      perror("setsockopt");
      exit(1);
    }

    if (bind(m_sockfd, next->ai_addr, next->ai_addrlen) == -1) {
      close(m_sockfd);
      perror("server: bind");
      continue;
    }

    break;
  }

  freeaddrinfo(servinfo);

  if (next == NULL) {
    std::cerr << "server: failed to bind\n";
    exit(1);
  }

  if (listen(m_sockfd, m_connection_limit) == -1) {
    perror("listen");
    exit(1);
  }
}

void Connection::accept_connection() {
  std::cout << "Waiting for connections...\n";

  while (1) {
    socklen_t sin_size = sizeof m_client_addr;
    m_clientfd = accept(m_sockfd, (struct sockaddr *)&m_client_addr, &sin_size);
    if (m_clientfd == -1) {
      perror("accept");
      continue;
    }

    char s[INET6_ADDRSTRLEN];
    inet_ntop(m_client_addr.ss_family, &(((struct sockaddr_in*)(struct sockaddr *)&m_client_addr)->sin_addr), s, sizeof s);
    std::cout << "Connection accepted from " << s << "\n";
    return;
  }
}

std::string Connection::receive_string() {
  char buf[m_receive_char_limit];
  int numbytes;
  if ((numbytes = recv(m_clientfd, buf, m_receive_char_limit-1, 0)) == -1) {
    perror("recv");
    exit(1);
  }

  buf[m_receive_char_limit] = '\0';

  return std::string(buf);
}

void Connection::send_string(std::string response) {
  if (send(m_clientfd, response.c_str(), response.length(), 0) == -1) {
    perror("send");
    return; // error handling
  }
}

void Connection::close_connection(std::string response) {
  send_string(response);
  close(m_clientfd);
}

void Connection::close_socket() {
  close(m_sockfd);
}


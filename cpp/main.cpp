#include <iostream>

#include "server.h"
#include "connection.h" // REMOVE THIS IMPORT

bool is_pos_num(const std::string &digit_string) {
  // No need to check for negatives as a negative port number would be invalid
  return digit_string.find_first_not_of("0123456789") == std::string::npos;
}

bool arguments_validated(int argc, char* argv[]) {
  return argc == 3 && !std::string(argv[1]).compare("-p") && is_pos_num(argv[2]);
}

void run_server(std::string port) {
  // Call a server class and pass port to the constructor
  Server server = Server(port);
  server.start();
  std::cout << server.process_request();
  server.close();
  // Start a while loop and try getting the result of a request and printing it
  // Catch and handle keyboard interrupt signals and return after cleaning up and printing a message
}

int main(int argc, char* argv[]) {
  
  std::string port = "8000";
  std::string usage = "Usage: request_parser [-p] [port-number]\n";

  if (argc > 1) {
    if (arguments_validated(argc, argv)) {
      port = argv[2];
    } else {
      std::cout << usage;
      return 1;
    }
  }

  Connection connection = Connection(port, 1, 1024);
  connection.start();
  connection.accept_connection();
  std::cout << connection.receive_string() << "\n";
  connection.close_connection("HTTP/1.1 204 NO-CONTENT\r\n\r\n");
  connection.close_socket();

  run_server(port);

  return 0;
}

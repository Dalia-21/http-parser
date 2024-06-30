#include <iostream>

const int DEFAULT_PORT = 8000;

bool is_pos_num(const std::string &digit_string) {
  // No need to check for negatives as a negative port number would be invalid
  return digit_string.find_first_not_of("0123456789") == std::string::npos;
}

bool arguments_validated(int argc, char* argv[]) {
  return argc == 3 && !std::string(argv[1]).compare("-p") && is_pos_num(argv[2]);
}

void run_server(int port) {
  // Call a server class and pass port to the constructor
  // Start a while loop and try getting the result of a request and printing it
  // Catch and handle keyboard interrupt signals and return after cleaning up and printing a message
}

int main(int argc, char* argv[]) {
  
  int port = DEFAULT_PORT;
  std::string usage = "Usage: request_parser [-p] [port-number]\n";

  if (argc > 1) {
    if (arguments_validated(argc, argv)) {
      port = std::stoi(argv[2]);
    } else {
      std::cout << usage;
      return 1;
    }
  }

  run_server(port);

  return 0;
}

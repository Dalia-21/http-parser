#!/opt/homebrew/bin/python3.12

import sys
import argparse

from server import Server


DEFAULT_PORT = 8000


def main(server: Server) -> None:
    server.start()

    while True:
        try:
            print(server.accept_request())
        except KeyboardInterrupt:
            server.close()
            sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int)
    args = parser.parse_args()
    
    port = DEFAULT_PORT
    if args.port:
        port = args.port
    server = Server(port)
    main(server)


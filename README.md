# HTTP Parser

A project to parse incoming HTTP requests and print their components to the console.

## Scope

The scope of this project has been deliberately kept small. The aim is to be able to receive a basic `GET` or `POST` request and display the request line parts, the headers, and the body. Some logic has been included to allow working with telnet, which sends chunks as individual lines. This means that a connection will not be closed until the end of the headers have been received, indicated by the characters `\r\n\r\n`, and in the case of a `POST` request, data equal to the length of the `Content-Length` header has been received.

Very little error handling has been included at this stage. This means if a completely invalid request is sent, the program will crash. If the headers are never completed, or no `Content-Length` header has been sent with a `POST` request, the program will wait for the client indefinitely. The program will also crash if an invalid character is sent by `telnet` when the program is exited. The program does not time out if no data is sent by the client, and it does not accept multiple requests, nor queued connections.

The purpose of this program is simply as an educational exercise, allowing for the examination of the contents of a basic `HTTP` request. As such, it is expected to be used at the console in conjunction with a program to send a request, whether this be `curl`, `telnet` or a browser client.

By default the program sends the most basic `204 NO-CONTENT` response to the client, and closes the socket, as the response is not the focus of this program. As a result, a browser will load an empty page. This behaviour is not expected to change, as the scope of this program is meant to be small.

## Implementations

### Python

The first implementation has been made in Python, for ease of prototyping. The program logic could be improved, as it currently relies on an excessive number of state variables. For a first implementation, it is adequate. This may be improved in future. The program structure has been kept quite simple. The main program simply initialises a `Server` object and asks it to accept a request. The `Server` will return a fully parsed and joined request string, only once it has determined that transmission is complete.

The main method which the server itself exposes then runs in a loop, receiving chunks from a client, and passing those chunks to a `Parser`. The `Parser` is responsible for tracking which components of the request have been received, and reporting whether the request is complete or not. The `Server` will terminate the connection once the request is complete, and return to the main program. The main program will then immediately request the `Server` to accept another request. The `Server` will wait until a connection is accepted, then repeat this process.

This cycle continues until an interrupt signal is sent to the main program, at which point it will gracefully shut down.


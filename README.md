# HTTP Parser

A project to parse incoming HTTP requests and print their components to the console.

## Scope

The scope of this project has been deliberately kept small. The aim is to be able to receive a basic `GET` or `POST` request and display the request line parts, the headers, and the body. Some logic has been included to allow working with telnet, which sends chunks as individual lines. This means that a connection will not be closed until the end of the headers have been received, indicated by the characters `\r\n\r\n`, and in the case of a `POST` request, data equal to the length of the `Content-Length` header has been received.

Very little error handling has been included at this stage. This means if a completely invalid request is sent, the program will crash. If the headers are never completed, or no `Content-Length` header has been sent with a `POST` request, the program will wait for the client indefinitely. The program does not time out if no data is sent by the client, and it does not accept multiple requests, nor queued connections.

The purpose of this program is simply as an educational exercise, allowing for the examination of the contents of a basic `HTTP` request. As such, it is expected to be used at the console in conjunction with a program to send a request, whether this be `curl`, `telnet` or a browser client.

By default the program sends the most basic `204 NO-CONTENT` response to the client, and closes the socket, as the response is not the focus of this program. As a result, a browser will load an empty page. This behaviour is not expected to change, as the scope of this program is meant to be small.

## Implementations

### Python

The first implementation has been made in Python, for ease of prototyping. The program structure has been kept quite simple. The main program simply initialises a `Server` object and asks it to accept a request. The `Server` will return a fully parsed and joined request string, only once it has determined that transmission is complete.

The method which the server itself exposes then runs in a loop, receiving chunks from a client, and passing those chunks to a `Parser`. The `Parser` is responsible for tracking which components of the request have been received, and reporting whether the request is complete or not. The `Server` will terminate the connection once the request is complete, and return to the main program. The main program will then immediately request the `Server` to accept another request. The `Server` will wait until a connection is accepted, then repeat this process.

This cycle continues until an interrupt signal is sent to the main program, at which point it will gracefully shut down.

### C++

The C++ implementation has been created as an opportunity to teach me more about C++. I'm interested in understanding this language better in order to give me a more comprehensive understanding of object oriented programming, since C++ implements classes in quite a low-level fashion.

A new class has been added in this case, `Connection`, because the code to set up a socket and listen for connections is significantly more complicated in C++. C++ uses the UNIX system calls directly, making the code much more verbose, so it seemed easier to store this code in a separate class, and allow the server code to focus on the application specific requirements.

The `Server` class focuses on repeatedly waiting for chunks of text from a user until a complete HTTP request has been identified. The `Connection` class on the other hand, provides access to a socket for listening, which could be reused outside of this purpose, so it seemed better to separate the two.

## Design Considerations

The design of this program, in both implementations, can be broken down into several discrete components. First, there is the main program, which accepts an optional port number from the user, and then starts the server. This program also handles keyboard interruptions from the user.

The rest of the program logic is split between the `Server` and the `Parser`. There is a certain amount of unavoidable coupling between these two classes, primarily through the interplay between the `Server` receiving a chunk of text, and the `Parser` reporting whether the request has been completed. In an ideal scenario, the `Server` could receive an entire request from the user, then pass it once to the `Parser` before returning the result to the main program.

The reason this is not possible, and the two need to communicate back and forth, is due to the nature of the network stack it sits on top of. In the case of a short, discrete request, the `Server` could indeed receive the full request before parsing it. In the case of a request larger than the maximum buffer size, however, or in the case of a `telnet` request, which comes through one line at a time, there is no way for the `Server` to know when the request is complete.

No special character is used in an HTTP request to signal the end of a request, and this character would do no good in the case of an improperly terminated request anyway. The presence of two newlines can only be relied on to signal the end of a request in the case of certain HTTP methods. The only way to properly identify the end of a request is to parse it. Parsing the request to identify the end of it before sending it to the `Parser` would entail significant duplicate calculation. For that reason, the best solution seemed to be to hand the request to the `Parser` one chunk at a time and rely on the `Parser` to report when the request is complete.


import socket
import sys

port = int(sys.argv[1]) if len(sys.argv) > 1 else 28333

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", port))
s.listen()


while 1:
    new_conn = s.accept()
    new_socket = new_conn[0]
    request_data = ""

    while 1:

        d = new_socket.recv(4096)
        text = d.decode("ISO-8859-1")

        request_data += text
        crlf = "\r\n\r\n"
        if crlf in text:
            string = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 6\r\nConnection: close\r\n\r\nHello!\r\n"
            b = string.encode("ISO-8859-1")
            new_socket.sendall(b)
            new_socket.close()
            break

    print(request_data)

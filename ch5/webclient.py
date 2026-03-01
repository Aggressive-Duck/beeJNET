import socket
import sys

domain = sys.argv[1] if len(sys.argv) > 1 else "google.com"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 80

s = socket.socket()
target = (domain, port)
s.connect(target)

string = "GET / HTTP/1.1\r\nHost: google.com\r\nConnection: close\r\n\r\nHello!"
b = string.encode("ISO-8859-1")

s.sendall(b)
while(1):
    d = s.recv(4096)
    print(d.decode("ISO-8859-1"))
    if len(d) == 0:
        break



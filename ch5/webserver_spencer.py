import socket


string = "GET / HTTP/1.1\r\nHost: google.com\r\nConnection: close\r\n\r\n"

ss = socket.socket()
ss.connect(("google.com", 80))
ss.sendall(string.encode("ISO-8859-1"))
while(1):
    d = ss.recv(4096)
    print(d.decode("ISO-8859-1"))
    if len(d) == 0:
        
        ss.close()
        break

#so good

import socket
import sys
import os

port = int(sys.argv[1]) if len(sys.argv) > 1 else 28333

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", port))
s.listen()

mime_codes_dic = {
    ".txt": "text/plain",
    ".html": "text/html",
}

# strip the file path


def parse_request_path(request_text):
    request_list = request_text.split("\r\n")
    request_path = request_list[0].split(" ")[1]
    request_file = os.path.split(request_path)[-1]
    return request_file


def generate_response(request_file):
    return_headers = ""
    connection_close = "Connection: close\r\n\r\n"
    file_extention = os.path.splitext(request_file)[-1]
    mime_type = mime_codes_dic.get(file_extention, "application/octet-stream")
    try:
        with open(request_file, "rb") as fp:
            body = fp.read()
            header = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n"
            return header.encode("ISO-8859-1") + body
    except FileNotFoundError:
        body = b"404 not found"  # why use bytes here
        header = f"HTTP/1.1 404 Not Found\r\nContent-Type: {mime_type}\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n"
        return header.encode("ISO-8859-1") + body


while 1:
    new_conn = s.accept()
    new_socket = new_conn[0]
    request_text = ""

    while 1:
        d = new_socket.recv(4096)
        text = d.decode("ISO-8859-1")

        request_text += text
        crlf = "\r\n\r\n"
        if crlf in text:
            break

    request_file = parse_request_path(request_text)
    response = generate_response(request_file)
    new_socket.sendall(response)
    new_socket.close()
    print(request_text)

# TODO: add second file

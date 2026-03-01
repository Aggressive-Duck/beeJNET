import socket
import sys

port = int(sys.argv[1]) if len(sys.argv) > 1 else 28333

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", port))
s.listen()

print(f"[*] Server listening on http://localhost:{port} ...")

try:
    while True: # 🔴 OUTER LOOP: Wait for a new client
        client_socket, client_addr = s.accept()
        
        request_data = ""
        
        while True: # 🔵 INNER LOOP: Download the request
            chunk = client_socket.recv(4096).decode("ISO-8859-1")
            
            if not chunk: # Client dropped connection
                break 
                
            request_data += chunk
            
            # Beej's Rule: Stop downloading the moment Headers end!
            if "\r\n\r\n" in request_data:
                break
        
        # Prevent crash if an empty connection is made
        if not request_data:
            client_socket.close()
            continue
            
        # ✂️ Split the data cleanly into 3 parts
        headers, separator, body = request_data.partition("\r\n\r\n")
        
        print("=== 📩 INCOMING HEADERS ===")
        print(headers)
        print("=== 📦 EXTRA BODY CAUGHT ===")
        print(repr(body)) # repr() shows hidden characters like \n
        
        # 🚀 Send the response
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 6\r\nConnection: close\r\n\r\nHello!"
        client_socket.sendall(response.encode("ISO-8859-1"))
        
        # 👋 Hang up the phone
        client_socket.close()

except KeyboardInterrupt:
    print("\n[!] Ctrl+C detected. Shutting down gracefully...")
finally:
    s.close()
import socket, sys
try:
    s = socket.socket()
    s.settimeout(3)
    s.connect(("localhost", 8000))
    s.sendall(b"GET /health HTTP/1.0\r\nHost: l\r\n\r\n")
    r = s.recv(256)
    s.close()
    sys.exit(0 if b"200" in r else 1)
except Exception:
    sys.exit(1)

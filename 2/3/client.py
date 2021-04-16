import socket

s = socket.socket()
port = 3125
s.connect(('localhost', port))
message = input("Please enter your message")
s.sendall(message.encode())    
s.close()
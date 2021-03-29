import socket


try: 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Socket created!")
except socket.error as err: 
    print (f"socket creation failed because of error {err}!")
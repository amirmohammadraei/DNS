import socket
import binascii


def send_message(message, address, port):
    server_address = (address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.sendto(message, server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    return binascii.hexlify(data).decode("utf-8")

if __name__ == '__main__':
    port = 53
    address = '8.8.8.8'
    message = str.encode('salam, khubi?')
    response = send_message(message, address, port)
    print(response)
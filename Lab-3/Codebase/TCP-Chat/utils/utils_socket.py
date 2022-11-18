from socket import socket, AF_INET, SOCK_STREAM

def get_socket():
    return socket(AF_INET, SOCK_STREAM)

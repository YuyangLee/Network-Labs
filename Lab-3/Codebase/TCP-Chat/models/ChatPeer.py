from socket import socket, AF_INET, SOCK_STREAM
import logging
from utils.utils_socket import get_socket

class ChatPeer:
    def __init__(self, type: str, name: str, id: str):
        self.type = type
        self.name = name
        self.id = id

        type = type.upper()
        if type in ['SERVER', 'CLIENT']:
            self.type = type
        else:
            raise NotImplementedError("Argument 'type' must be either 'SERVER' or 'CLIENT'.")
        
        self.identify_string = f"{ self.type } { self.name }({ self.id })"
        
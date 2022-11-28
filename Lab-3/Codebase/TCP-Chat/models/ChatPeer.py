import logging
from asyncio import Event
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

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
        
        

class SendThread(Thread):
    def __init__(self, conn_socket: socket, msg_str: str, handler=None, fail_handler=None):
        super().__init__()
        
        self.conn_socket = conn_socket
        self.msg_str = msg_str
        self.handler = handler
        self.fail_handler = fail_handler
        
    def run(self):
        try:
            self.conn_socket.send(self.msg_str.encode('utf-8'))
            logging.info(f"Sent message to { self.conn_socket.getpeername() }")
            
            if self.handler is not None:
                self.handler(self.conn_socket)
        except Exception as ex:
            logging.error(f"Failed to send message. { ex }")
            if self.fail_handler is not None:
                self.fail_handler(None)
                
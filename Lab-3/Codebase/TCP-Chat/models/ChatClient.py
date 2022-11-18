import json
import logging
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from models.ChatPeer import ChatPeer
from models.Message import Message


class ChatClient(ChatPeer):
    def __init__(self, client_name, client_id, server_addr, server_port)
        super().__init__("CLIENT", client_name, client_id)
        
        self.log = logging.getLogger(__name__)
        self.log.log(f"{ self.type } { self.name }(ID: { self.id }) initialized.")

        self.set_server(server_addr, server_port)

    def set_server(self, server_addr, server_port):
        self.server_addr = server_addr
        self.server_port = server_port
    
    def start(self):
        try:
            self.client_server = socket(AF_INET, SOCK_STREAM)
            self.client_server.connect((self.server_addr, self.server_port))
            MsgRecvThread(self.client_server, self.on_recv_msg, max_msg_len=1024).start()
            self.log.log(f"Connected to server at { self.server_addr }:{ self.server_port }")
        except Exception as ex:
            self.log.error(f"Failed to connect to server at { self.server_addr }:{ self.server_port }. { ex }")
        
    def on_recv_msg(self, msg_str: str):
        msg = Message(json.loads(msg_str))
        print(msg.to_display_str)
        
    def on_send_msg(self, msg):
        pass
    
class MsgRecvThread(Thread):
    def __init__(self, conn_socket: socket, handler, log, max_msg_len=1024):
        super().__init__()
        
        self.log = log
        self.conn_socket = conn_socket
        self.max_msg_len = max_msg_len
        
    def run(self):
        while True:
            try:
                msg_str = self.conn_socket.recv(self.max_msg_len).decode('utf-8')
                self.handler(msg_str)
                self.log.log(f"Received message from { self.conn_socket.getpeername() }.")
            except Exception as ex:
                self.log.error(f"Failed to receive message from server. { ex }")
                return
                
class MsgSendThread(Thread):
    def __init__(self, conn_socket: socket, msg: Message, log, max_msg_len=1024):
        super().__init__()
        
        self.log = log
        self.msg = msg
        self.conn_socket = conn_socket
        self.max_msg_len = max_msg_len
        
    def run(self):
        try:
            self.conn_socket.send(self.msg.to_json_str().encode('utf-8'))
            self.log.log(f"Sent message to { self.conn_socket.getpeername() }.")
        except Exception as ex:
            self.log.error(f"Failed to send message to server. { ex }")
            
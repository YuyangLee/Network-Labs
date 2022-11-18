import json
from socket import socket, AF_INET, SOCK_STREAM
import logging
from threading import Thread
from models.ChatPeer import ChatPeer
from models.Message import Message
from utils.utils_socket import get_socket

class ChatServer(ChatPeer):
    def __init__(self, server_name, server_id, server_addr='', server_port=20000):
        super().__init__("SERVER", server_name, server_id)
        
        self.log = logging.getLogger(__name__)
        self.log.log(f"{ self.type } { self.name }(ID: { self.id }) initialized.")
        
        self.welcome_socket = get_socket()
        self.__bind_addr = server_addr
        self.__bind_port = server_port
        try:
            self.welcome_socket.bind((self.__bind_addr, self.__bind_port))
            self.log.log(f"{self.identify_string} binded to [{ self.bind_addr}:{ self.bind_port }].")
        except Exception as ex:
            pass
        
    def start(self):
        self.client_pool = []
        listen_thread = ServerListenThread(self.welcome_socket, self.on_recv_conn, self.log, long=False, max_msg_len=1024)
        listen_thread.start()
        
    # def stop(self):
    #     for client_thread in self.client_pool:
    #         client_thread.stop()
    #     self.welcome_socket.close()

    def on_recv_conn(self, conn_socket: socket):
        try:
            res = conn_socket.recv(1024)
            msg_dict = json.loads(res.decode('utf-8'))
            if msg_dict['type'] == 'CTL':
                self.client_pool.append(ServerRecvThread(conn_socket, self.on_recv_msg, max_msg_len=1024))
                self.log.log(f"Connected to client at socket { socket.getsockname }")
            else:
                raise Exception("Invalid message type. Connection socket should be in a CTL message.")
        except Exception as ex:
            self.log.error(f"Received invalid message from client. { ex }")
        
    def on_recv_msg(self, msg_json_str: str, addr: str):
        try:
            msg_dict = json.loads(msg_json_str)
            msg = Message(msg_dict)
            
            sender_name, sender_ip, send_time, body = msg.unpack()
            body_hash = msg.get_body_hash()
            self.log.log(f"Ceceived message from { sender_name }({ sender_ip }). Message was sent at { send_time }. Message body MD5: { body_hash }")
            self.broadcast_msg(msg)
        except Exception as ex:
            self.log.error(f"Ceceived invalid message from client. Message: { msg_json_str }")
    
    def broadcast_msg(self, client_socket: socket, msg: Message, handler=None):
        msg_json = msg.to_json_str()
        
        for client_socket in self.client_pool:
            SendThread(client_socket, msg_json, log=self.log, handler=handler, fail_handler=self.rm_conn_socket).start()
            
    def rm_conn_socket(self, rm_socket: socket):
        self.client_pool.remove(rm_socket)
        
            
class ServerListenThread(Thread):
    def __init__(self, welcome_socket: socket, recv_handler, log, long=True):
        super().__init__()
        
        self.welcome_socket = welcome_socket
        self.recv_handler = recv_handler
        self.long = long
        self.log = log
        
    def run(self):
        while True:
            try:
                conn_socket, addr = self.welcome_socket.accept()
                self.recv_handler(conn_socket, addr)
            except:
                self.log.log(f"Received an error connection from { addr }.")

class ServerRecvThread(Thread):
    def __init__(self, conn_socket: socket, recv_handler, max_msg_len=1024):
        super().__init__()
        
        self.conn_socket = conn_socket
        self.recv_handler = recv_handler
        self.max_msg_len = max_msg_len
        
    def run(self):
        while True:
            try:
                msg_json_str = self.conn_socket.recv(self.max_msg_len).decode('utf-8')
                self.recv_handler(msg_json_str)
            except Exception as ex:
                self.log.error(f"Received invalid message from client. { ex }")
                break

class SendThread(Thread):
    def __init__(self, conn_socket: socket, msg_str: str, log, handler=None, fail_handler=None):
        super().__init__()
        self.conn_socket = conn_socket
        self.msg_str = msg_str
        self.log = log
        self.handler = handler
        self.fail_handler = fail_handler
        
    def run(self):
        try:
            self.conn_socket.send(self.msg_str.encode('utf-8'))
            self.log.log(f"Sent message to { self.conn_socket.getpeername() }")
            
            if self.handler is not None:
                self.handler(self.conn_socket)
        except Exception as ex:
            self.log.error(f"Failed to send message to { self.conn_socket.getpeername() }")
            self.conn_socket.close()
            if self.fail_handler is not None:
                self.fail_handler(self.conn_socket)

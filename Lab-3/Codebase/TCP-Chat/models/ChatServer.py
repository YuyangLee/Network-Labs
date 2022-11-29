import json
import logging
from datetime import datetime
from socket import *
from threading import Event, Thread

from utils.utils_id import gen_id
from utils.utils_socket import get_socket

from models.ChatPeer import ChatPeer, SendThread
from models.Message import Message, gen_message, gen_message_raw


class ChatServer(ChatPeer):
    def __init__(self, server_name, server_id, server_addr='', server_port=20000):
        super().__init__("SERVER", server_name, server_id)
        
        logging.info(f"{ self.type } { self.name }(ID: { self.id }) initialized. Started a low performance chat server.")
        
        self.welcome_socket = socket(AF_INET, SOCK_STREAM)
        self.__bind_addr = '' # server_addr
        self.__bind_port = server_port
        try:
            self.welcome_socket.bind(('', self.__bind_port))
            logging.info(f"{self.identify_string} binded to [{ self.__bind_addr}:{ self.__bind_port }].")
        except Exception as ex:
            pass
        
    def start(self):
        self.client_pool = {}
        self.exit_events = {}
        logging.info(f"{ self.identify_string } starts listening on port { self.__bind_addr }:{ self.__bind_port }.")
        listen_thread = ServerListenThread(self.welcome_socket, self.on_recv_conn, long=False)
        listen_thread.start()
        
    def stop(self):
        pass
    
    def on_recv_conn(self, conn_socket: socket):
        try:
            res = conn_socket.recv(1024)
            msg_dict = json.loads(res.decode('utf-8'))
            if msg_dict['type'] == 'CTL' and msg_dict['body'] == 'HELO':
                
                id = gen_id()
                while id in self.client_pool:
                    id = gen_id()
                    
                sender_ip, sender_port = conn_socket.getpeername()
                
                self.broadcast_sys_msg(f"{ msg_dict['sender_name'] }({ sender_ip }) is now online!", except_list=[id])
                
                # Bradcast before connecting to remove last connection. Can be remedied with keep alive or sth like that...
                
                self.exit_events[id] = Event()                    
                self.client_pool[id] = conn_socket
                ServerRecvThread(self.exit_events[id], id, conn_socket, self.on_recv_msg, max_msg_len=1024).start()
            
            else:
                raise Exception("Invalid message type. Connection socket should be in a CTL message with \"HELO\".")
        except Exception as ex:
            logging.error(f"Received invalid message from client. { ex }")
        
    def on_recv_msg(self, from_conn_id: str, msg: Message):
        try:
            sender_name, send_time, body, sender_ip, sender_port, type= msg.unpack()
            logging.info(f"Received { type } message from { sender_name }({ sender_ip }:{ sender_port }). Message was sent at { send_time }.")
            
            if type == "MSG":
                self.broadcast_msg(msg, [from_conn_id])
                
            elif type == "CTL" and body == "BYE":
                self.broadcast_sys_msg(f"{ sender_name }({ sender_ip }) is now offline!", except_list=[from_conn_id])
                self.disconn_socket(from_conn_id)
                
        except Exception as ex:
            logging.error(f"Received invalid message from client. Message: { ex }")
    
    def broadcast_msg(self, msg: Message, except_list: list, handler=None):
        msg_json = msg.to_json_str()
        
        for conn_id, client_socket in self.client_pool.items():
            if conn_id in except_list:
                continue
            SendThread(client_socket, msg_json, handler=handler, fail_handler=lambda x: self.disconn_socket(conn_id)).start()
            
    def broadcast_sys_msg(self, msg_str: str, except_list: list, handler=None):
        msg = gen_message_raw("System", msg_str, "MSG", sender_ip=None, sender_port=None, send_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.broadcast_msg(msg, except_list, handler)
            
    def disconn_socket(self, from_conn_id: str):
        if from_conn_id in self.exit_events:
            self.exit_events[from_conn_id].set()
            del self.exit_events[from_conn_id]
            
        if from_conn_id in self.client_pool:
            try:
                self.client_pool[from_conn_id].shutdown(SHUT_RDWR)
            finally:
                del self.client_pool[from_conn_id]
            logging.info(f"Removed connection socket { from_conn_id } from client pool.")
        
            
class ServerListenThread(Thread):
    def __init__(self, welcome_socket: socket, recv_handler, long=True):
        super().__init__()
        
        self.welcome_socket = welcome_socket
        self.recv_handler = recv_handler
        self.long = long
        self.conn_id = gen_id()
        
    def run(self):
        self.welcome_socket.listen(1)
        while True:
            try:
                conn_socket, addr = self.welcome_socket.accept()
                logging.info(f"Accepted connection from { addr }")
                self.recv_handler(conn_socket)
            except:
                pass

class ServerRecvThread(Thread):
    def __init__(self, exit_event: Event, conn_id: str, conn_socket: socket, recv_handler, max_msg_len=1024):
        super().__init__()
        
        self.exit_event = exit_event
        self.conn_id = conn_id
        self.conn_socket = conn_socket
        
        self.recv_handler = recv_handler
        self.max_msg_len = max_msg_len
        self.peer, self.tg_port = conn_socket.getpeername()
        
        logging.info(f"Started to receive message from { self.peer }:{ self.tg_port } via connection { self.conn_id }.")
        
    def run(self):
        while True:
            try:
                msg_json_str = self.conn_socket.recv(self.max_msg_len).decode('utf-8')
                msg_dict = json.loads(msg_json_str)
                msg_dict['sender_ip'] = self.peer
                msg_dict['sender_port'] = self.tg_port
                msg_dict['send_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                msg = gen_message(msg_dict)
                logging.info(f"Received message from client, broad casting...")
                self.recv_handler(self.conn_id, msg)
            except Exception as ex:
                if self.exit_event.is_set():
                    logging.info(f"Connection { self.conn_id } is now closed.")
                    break
                logging.error(f"Received invalid message from client. { ex }")
                break

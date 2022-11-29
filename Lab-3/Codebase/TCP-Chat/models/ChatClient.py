import json
import logging
import re
from socket import *
from threading import Event, Thread

from models.ChatPeer import ChatPeer, SendThread
from models.Message import Message, gen_message, gen_message_raw


class ChatClient(ChatPeer):
    def __init__(self, client_name, client_id, server_addr, server_port):
        super().__init__("CLIENT", client_name, client_id)
        
        logging.info(f"{ self.type } { self.name }(ID: { self.id }) initialized.")

        self.set_server(server_addr, server_port)

    def set_server(self, server_addr, server_port):
        self.server_addr = server_addr
        self.server_port = server_port
        
    def send_msg(self, msg_str: str, type='MSG'):
        try:
            msg = gen_message_raw(self.name, sender_ip="", send_time="", body=msg_str, type=type)
            msg_json = msg.to_json_str()
            SendThread(self.client_socket, msg_json).start()
        except Exception as ex:
            logging.error(f"Failed to send message. { ex }")
            return 1
        finally:
            return -1
    
    def start(self):
        try:
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            # self.client_socket.bind(('', bind_port))
            self.client_socket.connect((self.server_addr, self.server_port))
            logging.info(f"Connected to server at { self.server_addr }:{ self.server_port }")  
            
            self.exit_event = Event()
            self.recv_thrd = MsgRecvThread(self.exit_event, self.client_socket, self.on_recv_msg, max_msg_len=1024)
            self.recv_thrd.start()
            
            return -1
        except Exception as ex:
            logging.error(f"Failed to connect to server at { self.server_addr }:{ self.server_port }. { ex }")
            return 1
        
    def on_recv_msg(self, msg_str: str):
        msg = gen_message(json.loads(msg_str))
        print(msg.to_display_str())
        
    
    def stop(self):
        self.send_msg("BYE", type='CTL')
        self.client_socket.shutdown(SHUT_RDWR)
        self.exit_event.set()
    
    def execute_cmd(self, cmd, arg=None):
        if cmd == 'q':
            self.stop()
            logging.info(f"{ self.identify_string } stopped.")
            return 0
        raise Exception(f"Unknown command: { cmd }")            
    
    def parse_line(self, line):
        if line == "":
            return -1
        if line[:2] == "::":
            return self.send_msg(line[1:], type='MSG')
        if line[0] == ':':
            ca = re.match(r'([a-z]{1,3})\s(.*)', line[1:])
            if ca:
                cmd, arg = ca.groups()
                return self.execute_cmd(cmd, arg)
            c = re.match(r'([a-z]{1,3})', line[1:])
            if c:
                cmd, = c.groups()
                return self.execute_cmd(cmd, arg=None)
        else:
            return self.send_msg(line, type='MSG')
        
        return -1
    
class MsgRecvThread(Thread):
    def __init__(self, exit_event: Event, conn_socket: socket, handler, max_msg_len=1024):
        super().__init__()
        
        self.exit_event = exit_event
        self.handler = handler
        self.conn_socket = conn_socket
        self.max_msg_len = max_msg_len
        
    def run(self):
        while True:
            try:
                msg_str = self.conn_socket.recv(self.max_msg_len).decode('utf-8')
                self.handler(msg_str)
                logging.info(f"Received message from { self.conn_socket.getpeername() }.")
            except Exception as ex:
                if self.exit_event.is_set():
                    logging.info(f"Connection to server is now closed.")
                    return
                logging.error(f"Failed to receive message from server. { ex }")
                return
              
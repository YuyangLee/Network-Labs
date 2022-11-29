import hashlib
import json


def gen_message(msg_dict: dict):
    sender_name, body, type = msg_dict["sender_name"], msg_dict["body"], msg_dict["type"]
    sender_ip = msg_dict["sender_ip"] if 'sender_ip' in msg_dict else None
    sender_port = msg_dict["sender_port"] if 'sender_port' in msg_dict else None
    send_time = msg_dict["send_time"] if 'send_time' in msg_dict else None
    return Message(sender_name, body, type, sender_ip, sender_port, send_time)

def gen_message_raw(sender_name: str, body: str, type='MSG', sender_ip=None, sender_port=None, send_time=None):
    return Message(sender_name, body, type, sender_ip, sender_port, send_time)

class Message:
    def __init__(self, sender_name: str, body: str, type='MSG', sender_ip=None, sender_port=None, send_time=None):
        self.sender_name = sender_name
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.send_time = send_time
        self.body = body
        self.type = type
        
    def get_full_hash(self):
        md5 = hashlib.md5()
        full_msg = f"{ self.sender_name }{ self.send_time }{ self.body }"
        md5.update(full_msg.encode('utf-8'))
        return md5.hexdigest()
        
    def get_body_hash(self):
        md5 = hashlib.md5()
        md5.update(self.body.encode('utf-8'))
        return md5.hexdigest()
    
    def unpack(self):
        return self.sender_name, self.send_time, self.body, self.sender_ip, self.sender_port, self.type
    
    def to_json_str(self):
        msg_dict = {
            "type": self.type,
            "sender_name": self.sender_name,
            "sender_ip": self.sender_ip,
            "sender_port": self.sender_port,
            "send_time": self.send_time,
            "body": self.body
        }
        return json.dumps(msg_dict)
    
    def to_display_str(self) -> str:
        txt = f"[{ self.send_time }] { self.sender_name }"
        if self.sender_ip is not None:
            txt += f"({ self.sender_ip }:{ self.sender_port })"
        return txt + "\n" + self.body + "\n"
    
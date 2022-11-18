import hashlib
import json

class Message:
    def __init__(self, sender_name: str, sender_ip: str, send_time: str, body: str, type='MSG'):
        self.sender_name = sender_name
        self.sender_ip = sender_ip
        self.send_time = send_time
        self.body = body
        self.type = type
        
    def __init__(self, msg_dict: dict):
        self.sender_name = msg_dict["sender_name"]
        self.sender_ip = msg_dict["sender_ip"]
        self.send_time = msg_dict["send_time"]
        self.body = msg_dict["body"]
        self.type = msg_dict["type"]
        
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
        return self.sender_name, self.send_time, self.body, self.sender_ip
    
    def to_json_str(self):
        msg_dict = {
            "type": self.type,
            "sender_name": self.sender_name,
            "sender_ip": self.sender_ip,
            "send_time": self.send_time,
            "body": self.body
        }
        return json.dumps(msg_dict)
    
    def to_display_str(self) -> str:
        return f"""
[{ self.send_time }] { self.sender_name }({ self.sender_ip }):
{ self.body }

"""
    
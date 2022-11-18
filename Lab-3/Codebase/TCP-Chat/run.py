'''
Author: Aiden Li
Date: 2022-11-18 15:24:55
LastEditors: Aiden Li (i@aidenli.net)
LastEditTime: 2022-11-18 15:29:55
Description: Unified entry point for the TCP Chat application.
'''

import argparse
from uuid import uuid4
from models.ChatClient import ChatClient
from models.ChatServer import ChatServer

def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--mode", default='client', type=str)
    # parser.add_argument("--bind_addr", default="127.0.0.1", type=str)
    # parser.add_argument("--bind_port", default=10000, type=int)
    parser.add_argument("--server_addr", default="127.0.0.1", type=str)
    parser.add_argument("--server_port", default=20000, type=int)
    
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    
    if args.mode == 'server':
        server = ChatServer("ServerName", str(uuid4()), args.server_addr, args.server_port)
        server.start()
        
    elif args.mode == 'client':
        client = ChatClient("ClientName", str(uuid4()), args.server_addr, args.server_port)
        client.bind(args.bind_addr, args.bind_port)
        client.connect(args.server_addr, args.server_port)
        
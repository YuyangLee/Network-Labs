'''
Author: Aiden Li
Date: 2022-11-18 15:24:55
LastEditors: Aiden Li (i@aidenli.net)
LastEditTime: 2022-11-18 15:29:55
Description: Unified entry point for the TCP Chat application.
'''

import argparse
import logging
import os
from time import sleep

from utils.utils_id import gen_id


def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--mode", default='server', type=str)
    parser.add_argument("--server_addr", default="localhost", type=str)
    parser.add_argument("--server_port", default=12334, type=int)
    parser.add_argument("--name", default="Server", type=str)
    parser.add_argument("--log", default="log/server.log", type=str)
    
    return parser.parse_args()

def init(args):
    os.makedirs(os.path.dirname(args.log), exist_ok=True)
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=args.log, level=logging.DEBUG, format=LOG_FORMAT)
    
if __name__ == '__main__':
    args = get_args()
    
    init(args)

    
    if args.mode == 'server':
        from models.ChatServer import ChatServer
        server = ChatServer(args.name, gen_id(), args.server_addr, args.server_port)
        server.start()
        
    elif args.mode == 'client':
        from models.ChatClient import ChatClient
        client = ChatClient(args.name, gen_id(), args.server_addr, args.server_port)
        if client.start():
            client.send_msg("HELO", type='CTL')
        
        while True:
            line = input("")
            # line = input("$ ")
            flag = client.parse_line(line)

            if flag == -1:
                pass
            elif flag == 0:
                input("See you next time! Press ENTER to exit...")
                break
            elif flag == 1:
                input(f"Error occured! Please refer to the log at { args.log }. Press any key to exit...")
                print("")
            
            
        exit()
        
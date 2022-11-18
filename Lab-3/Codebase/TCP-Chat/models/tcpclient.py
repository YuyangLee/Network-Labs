from socket import *
import logging
import hydra
from threading import Thread


# 循环阻塞式地从socket中读取数据，必须放在一个独立的线程中，
# 否则，就没办法实现用户能够同时输入消息和程序实时打印接收到的消息
class ReceivingThread(Thread):
    def __init__(self):
        super().__init__()

    def run(self, clientSocket):
        while True:
            modifiedSentence = clientSocket.recv(1024)
            if len(modifiedSentence) == 0:
                # 返回的句子长度为0，说明对端已close
                clientSocket.close()
                return
            print('From Server:', modifiedSentence.decode())

def run(args):
    # 开启上面定义的线程
    receivingThread = ReceivingThread()
    receivingThread.start()

    sentence = input('Input lowercase sentence:')
    clientSocket.send(sentence.encode())

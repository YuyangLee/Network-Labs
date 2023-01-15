FLAG_NUL = 0x00
FLAG_FIN = 0x01
FLAG_SYN = 0x02
FLAG_RST = 0x04
FLAG_PSH = 0x08
FLAG_ACK = 0x10
FLAG_URG = 0x20

INIT=0x0
SYNSENT = 0x1
ESTABLISHED = 0x2
FINWAIT = 0x3
CLOSEWAIT = 0.04
FINWAIT2 = 0x5
CLOSING=0x6
TIMEWAIT=0x7
LASTACK=0x8
CLOSED=0x9

import math
from time import sleep
from api import app_peer_fin, app_peer_rst, app_recv, release_connection, tcp_tx, app_connected
from api_type import ConnectionIdentifier
from utils import ip_to_bytes, gen_checksum
from threading import Timer
from threading import Thread, Event
from queue import PriorityQueue

class CloseConnThread(Thread):
    def __init__(self, conn: ConnectionIdentifier, fsm, timeout=3000):
        Thread.__init__(self)
        self.timeout = timeout
        self.fsm = fsm
        self.conn = conn
        
    def run(self):
        sleep(self.timeout / 1000)
        self.fsm.state = LASTACK
        self.fsm.ack_n(2**31)
        release_connection(self.conn)
        self.fsm.state = CLOSED
        return

class SendPktThread(Thread):
    def __init__(self, ack_event: Event, conn: ConnectionIdentifier, data: bytes, timeout: int, callback=None):
        Thread.__init__(self)
        
        self.ack_event = ack_event
        self.timeout = timeout
        self.conn = conn
        self.data = data
        self.callback = callback
        # self.max_ticks = 50
        
    def run(self):
        print("A new thread is up")
        while True:
            # Timer(interval=self.timeout).start()
            sleep(self.timeout / 1000)
            if self.ack_event.is_set():
                break
            tcp_tx(self.conn, self.data)
            
        if self.callback:
            self.callback(self.conn)
        print("A new thread is closed")
        return


class TCPPacket:
    def __init__(self, src_port, dst_port, seq_num, ack_num, flags, window=64000, checksum=0x00, urgent_pointer=0x00, options=None, payload=""):
        self.src_port = src_port.to_bytes(2, 'big')
        self.dst_port = dst_port.to_bytes(2, 'big')
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.header_len = 20
        self.hlen = (self.header_len<<2).to_bytes(1, 'big')
        self.flags = flags # Used for AND operations, will not be converted here...
        self.window = window.to_bytes(2, 'big')
        self.checksum = checksum.to_bytes(2, 'big')
        self.urgent_pointer = urgent_pointer.to_bytes(2, 'big')
        self.tcp_protocol = (6).to_bytes(1, 'big')
        
        if isinstance(payload, str):
            self.payload = bytes(payload, encoding='utf-8')
        elif isinstance(payload, bytes):
            self.payload = payload
        else:
            self.payload = bytes(str(payload), encoding='utf-8')
            
        self.chunksize = 2
        self.zero = 0
        
        
    def to_bytes(self, pad_payload=0):
        header = self._header_bytes()
        return header + self.payload + b'\x00' * pad_payload
    
    def _header_bytes(self):
        header = self.src_port + self.dst_port + self.seq_num.to_bytes(4, 'big') + self.ack_num.to_bytes(4, 'big') + self.hlen + self.flags.to_bytes(1, 'big') + self.window + self.checksum + self.urgent_pointer
        # if self.options is not None:
        #     header += bytes(self.options, encoding='utf-8')
            
        return header
    
    def _pseudo_header(self, src_ip, dst_ip, len):
        src_ip = ip_to_bytes(src_ip)
        dst_ip = ip_to_bytes(dst_ip)
        reserved = self.zero.to_bytes(1, 'big')
        protocol = self.tcp_protocol
        length = len.to_bytes(2, 'big')
        
        pseudo_header = src_ip + dst_ip + reserved + protocol + length
        return pseudo_header
    
    # TODO: Length completion here may cause trouble!
    def gen_checksum(self, src_ip, dst_ip, update=True):
        payload = self.payload
            
        padding = self.chunksize - len(payload) % self.chunksize if (len(payload) % self.chunksize != 0) else 0
        
        pseudo_header = self._pseudo_header(src_ip, dst_ip, len(self))
        data = pseudo_header + self.to_bytes(pad_payload=padding)
        cksm = gen_checksum(data, chunksize=self.chunksize).to_bytes(2, 'big')
        
        if update:
            self.checksum = cksm
            # self.payload = payload
        else:
            return cksm
        
    def __len__(self):
        return self.header_len + len(self.payload)
    
class TCPFSM:
    def __init__(self, init_seq, timeout=1000, max_size=65535-40, win=32000):
        self.timeout = timeout
        self.win = win
        self.state = INIT
        self.sent_queue = PriorityQueue()
        self.seq_N = init_seq
        self.peer_N = 0
        # self.sent_N = init_seq
        self.max_size = max_size
    
    def _send_pkt(self, conn: ConnectionIdentifier, pkt: TCPPacket, callback=None, reliable=True):
        pkt.gen_checksum(conn['src']['ip'], conn['dst']['ip'])
        pkt_bytes = pkt.to_bytes()
        if reliable:
            event = Event()
            SendPktThread(event, conn, pkt_bytes, self.timeout, callback=callback).start()
            self.sent_queue.put((pkt.seq_num, event))
        else:
            tcp_tx(conn, pkt_bytes)
        self.seq_N += len(pkt.payload)
        print(f"Send, now SEQ = { self.seq_N }")
        
    # Connection Establishment
    def connect(self, conn: ConnectionIdentifier):
        self.send_syn(conn)
            
    def send_syn(self, conn: ConnectionIdentifier):
        ack = 0
        pkt = TCPPacket(conn['src']['port'], conn['dst']['port'], self.seq_N, ack, FLAG_SYN, window=self.win)
        self.seq_N += 1
        self._send_pkt(conn, pkt, reliable=False)
        
    def accept(self, conn: ConnectionIdentifier, pkt: TCPPacket):
        if pkt.flags & FLAG_SYN and pkt.flags & FLAG_ACK and pkt.ack_num == self.seq_N:
            self.peer_N = pkt.seq_num + 1
            self._accept_synack(conn, pkt)
            ack_pkt = TCPPacket(conn['src']['port'], conn['dst']['port'], self.seq_N, self.peer_N, FLAG_ACK, self.win)
            self._send_pkt(conn, ack_pkt, reliable=False)
        elif pkt.flags & FLAG_FIN:
            print("Received FIN")
            self._accept_fin(conn, pkt)
        elif pkt.flags & FLAG_ACK and self.state == FINWAIT and pkt.ack_num == self.seq_N:
            print("========FINWAIT========")
            self._accept_finack(conn, pkt)
        elif pkt.flags & FLAG_ACK and pkt.seq_num == self.peer_N:
            self.peer_N += len(pkt.payload)
            self._accept_upack(conn, pkt)
            print("UPACK")
            ack_pkt = TCPPacket(conn['src']['port'], conn['dst']['port'], self.seq_N, self.peer_N, FLAG_ACK, self.win)
            self._send_pkt(conn, ack_pkt, reliable=False)
        else:
            return 
        
        
    def _accept_synack(self, conn: ConnectionIdentifier, pkt: TCPPacket):
        app_connected(conn)
        self.state = ESTABLISHED
            
    # Data Transfer - Outgoing
    def send_data(self, conn: ConnectionIdentifier, data: bytes):
        parts = int(math.ceil(len(data) / self.max_size))
        flag = FLAG_ACK | FLAG_PSH
        for i in range(parts):
            _data = data[i*self.max_size:(i+1)*self.max_size]
            pkt = TCPPacket(conn['src']['port'], conn['dst']['port'], self.seq_N, self.peer_N, flag, self.win, payload=_data)
            self._send_pkt(conn, pkt)
            
    def _accept_upack(self, conn: ConnectionIdentifier, pkt: TCPPacket):
        self.ack_n(pkt.ack_num)
        
        if len(pkt.payload) > 0:
            app_recv(conn, pkt.payload)
        
    # Connection Termination
    def send_fin(self, conn: ConnectionIdentifier):
        self.state = FINWAIT
        fin_pkt = TCPPacket(conn['src']['port'], conn['dst']['port'], self.seq_N, self.peer_N, FLAG_FIN | FLAG_ACK, self.win)
        self.seq_N += 1
        self._send_pkt(conn, fin_pkt)
            
    def _accept_finack(self, conn: ConnectionIdentifier, pkt: TCPPacket):
        self.state = FINWAIT
        print(pkt.ack_num)
        self.ack_n(pkt.ack_num)
        
    def _accept_fin(self, conn: ConnectionIdentifier, pkt):
        if self.state == FINWAIT:
            print("Closing")
            self.peer_N = pkt.seq_num + 1
            ack_pkt = TCPPacket(conn['src']['port'], conn['dst']['port'], self.seq_N, self.peer_N, FLAG_ACK, self.win)
            self._send_pkt(conn, ack_pkt, reliable=False)
            CloseConnThread(conn, self, 3000).start()
        
        # TODO: Check pkt seq
        elif self.state == ESTABLISHED:
            print("Closing by peer")
            self.state = CLOSEWAIT
            ack_pkt = TCPPacket(conn['src']['port'], conn['dst']['port'], self.seq_N, pkt.seq_num, FLAG_ACK, self.win)
            self._send_pkt(conn, ack_pkt, reliable=False)
            self.state = LASTACK
            app_peer_fin(conn)
            syn_pkt = TCPPacket(conn['src']['port'], conn['dst']['port'], self.seq_N, pkt.seq_num, FLAG_FIN, self.win)
            self._send_pkt(conn, syn_pkt, callback=release_connection)
            release_connection(conn)
            CloseConnThread(conn, self, 3000).start()
        
    # Connection Reset
    def accept_rst(self, conn: ConnectionIdentifier, pkt: TCPPacket):
        self.ack_n(2e32-1)
        app_peer_rst(conn)

    def ack_n(self, n):
        while len(self.sent_queue.queue) > 0:
            seq, _ = self.sent_queue.queue[0]
            if seq > n:
                break
            seq, event = self.sent_queue.get()
            print(f"ACKed { seq }")
            event.set()

    def reset(self, conn: ConnectionIdentifier):
        # TODO: Implement reset logic
        app_peer_rst(conn)
        pass
    
    def tick(self):
        pass 
    
def parse_tcp_pkt(conn: ConnectionIdentifier, data: bytes):
    src_port, dst_port = int.from_bytes(data[:2], 'big'), int.from_bytes(data[2:4], 'big')
    seq_num, ack_num = int.from_bytes(data[4:8], 'big'), int.from_bytes(data[8:12], 'big')
    hlen = int.from_bytes(data[12:13], 'big') >> 2
    flags = int.from_bytes(data[13:14], 'big')
    window = int.from_bytes(data[14:16], 'big')
    checksum = int.from_bytes(data[16:18], 'big')
    urgent = int.from_bytes(data[18:20], 'big')
    options = int.from_bytes(data[20:hlen], 'big')
    
    payload = data[hlen:] if len(data) > hlen else ""
    
    pkt = TCPPacket(src_port, dst_port, seq_num, ack_num, flags, checksum=checksum, payload=payload)
    
    return pkt

    
if __name__ == '__main__':
    header = TCPPacket(
        2333, 2333,
        100, 1,
        FLAG_SYN, 6400,
        payload="Hello, it's me."
    )
    
    print(bytes(header))
    
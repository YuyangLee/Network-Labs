"""
这是等待你完成的代码。正常情况下，本文件是你唯一需要改动的文件。
你可以任意地改动此文件，改动的范围当然不限于已有的五个函数里。（只要已有函数的签名别改，要是签名改了main里面就调用不到了）
在开始写代码之前，请先仔细阅读此文件和api文件。这个文件里的五个函数是等你去完成的，而api里的函数是供你调用的。
提示：TCP是有状态的协议，因此你大概率，会需要一个什么样的数据结构来记录和维护所有连接的状态
"""
from api import ConnectionIdentifier, release_connection
from api_type import conn_to_str
import tcp
from tcp import TCPFSM, TCPPacket, parse_tcp_pkt

fsms = {}

def app_connect(conn: ConnectionIdentifier):
    """
    当有应用想要发起一个新的连接时，会调用此函数。想要连接的对象在conn里提供了。
    你应该向想要连接的对象发送SYN报文，执行三次握手的逻辑。
    当连接建立好后，你需要调用app_connected函数，通知应用层连接已经被建立好了。
    :param conn: 连接对象
    :return: 
    """
    if conn['dst']['ip'] == "127.0.0.1":
        return
    print("app_connect", conn)
    conn_id = conn_to_str(conn)
<<<<<<< HEAD
    fsms[conn_id] = TCPFSM(init_seq=1000, timeout=1000, win=32000)
=======
    fsms[conn_id] = TCPFSM(init_seq=1000, timeout=1000, win=64000)
>>>>>>> 2de310c6cb8ce5f77615981537208a36de7ad5f6
    fsm = fsms[conn_id]
    
    fsm.connect(conn)


def app_send(conn: ConnectionIdentifier, data: bytes):
    """
    当应用层想要在一个已经建立好的连接上发送数据时，会调用此函数。
    :param conn: 连接对象
    :param data: 数据内容，是字节数组
    :return:
    """
    conn_id = conn_to_str(conn)
    fsm = fsms[conn_id]
    
    fsm.send_data(conn, data)
    print("app_send", conn)
    # print("app_send", conn, data.decode(errors='replace'))


def app_fin(conn: ConnectionIdentifier):
    """
    当应用层想要半关闭连接(FIN)时，会调用此函数。
    :param conn: 连接对象
    :return: 
    """
    print("app_fin", conn)
    conn_id = conn_to_str(conn)
    fsm = fsms[conn_id]
    
    fsm.send_fin(conn)
    
<<<<<<< HEAD
=======
    release_connection(conn)

>>>>>>> 2de310c6cb8ce5f77615981537208a36de7ad5f6

def app_rst(conn: ConnectionIdentifier):
    """
    当应用层想要重置连接(RES)时，会调用此函数
    :param conn: 连接对象
    :return: 
    """
    print("app_rst", conn)
    conn_id = conn_to_str(conn)
    fsm = fsms[conn_id]
    
    fsm.reset(conn)
    


def tcp_rx(conn: ConnectionIdentifier, data: bytes):
    """
    当收到TCP报文时，会调用此函数。
    正常情况下，你会对TCP报文，根据报文内容和连接的当前状态加以处理，然后调用0个~多个api文件中的函数
    :param conn: 连接对象
    :param data: TCP报文内容，是字节数组。（含TCP报头，不含IP报头）
    :return: 
    """
    print("tcp_rx", conn)
    pkt = parse_tcp_pkt(conn, data)
    conn_id = conn_to_str(conn)
    fsm = fsms[conn_id]
    
    # Broken package, ignore
<<<<<<< HEAD
    # if not pkt.gen_checksum(conn['src']['ip'], conn['dst']['ip']) == bytes('1111111111111111', encoding='utf-8'):
    #     return
    
    fsm.accept(conn, pkt)
=======
    # if not pkt.gen_checksum(conn['src']['ip'], conn['dst']['ip']) == bytes('1111111111111111'):
    #     return
    
    fsm.accept(conn, pkt)
    
    # if pkt.flags & tcp.FLAG_ACK:
    #     fsm.accept_ack(conn, pkt)
        
    # elif pkt.flags & tcp.FLAG_FIN:
    #     fsm.accept_fin(conn, pkt)
        
    # elif pkt.flags & tcp.FLAG_RST:
    #     fsm.accept_rst(conn, pkt)
        
    # else:
    #     fsm.recv_seq(conn, pkt)
    # print("tcp_rx", conn, data.decode(errors='replace'))
>>>>>>> 2de310c6cb8ce5f77615981537208a36de7ad5f6

def tick():
    """
    这个函数会每至少100ms调用一次，以保证控制权可以定期的回到你实现的函数中，而不是一直阻塞在main文件里面。
    它可以被用来在不开启多线程的情况下实现超时重传等功能，详见主仓库的README.md
    """
    # TODO 可实现此函数，也可不实现
    rm_conn_id = []
    for conn_id, fsm in fsms.items():
        if fsm.state == tcp.CLOSED:
            rm_conn_id.append(conn_id)
            continue
        fsm.tick()     
        
    for conn_id in rm_conn_id:
        print(f"Removed{conn_id}")
        del fsms[conn_id]

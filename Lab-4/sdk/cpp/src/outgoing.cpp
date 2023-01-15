/**
 * 这是等待你完成的代码。正常情况下，本文件是你唯一需要改动的文件。
 * 你可以任意地改动此文件，改动的范围当然不限于已有的五个函数里。（只要已有函数的签名别改，要是签名改了main里面就调用不到了）
 * 在开始写代码之前，请先仔细阅读此文件和api文件。这个文件里的五个函数是等你去完成的，而api里的函数是供你调用的。
 * 提示：TCP是有状态的协议，因此你大概率，会需要一个什么样的数据结构来记录和维护所有连接的状态
 */
#include "outgoing.h"

/**
 * 当有应用想要发起一个新的连接时，会调用此函数。想要连接的对象在conn里提供了。
 * 你应该向想要连接的对象发送SYN报文，执行三次握手的逻辑。
 * 当连接建立好后，你需要调用app_connected函数，通知应用层连接已经被建立好了。
 * @param conn 连接对象
 */
void app_connect(ConnectionIdentifier &conn) {
    // TODO 请实现此函数
    std::cout << "app_connect" << conn << std::endl;
}

/**
 * 当应用层想要在一个已经建立好的连接上发送数据时，会调用此函数。
 * @param conn 连接对象
 * @param bytes 数据内容，是字节数组
 */
void app_send(ConnectionIdentifier &conn, std::vector<uint8_t> &bytes) {
    // TODO 请实现此函数
    std::cout << "app_send" << conn << bytes.data() << std::endl;
}

/**
 * 当应用层想要半关闭连接(FIN)时，会调用此函数。
 * @param conn 连接对象
 */
void app_fin(ConnectionIdentifier &conn) {
    // TODO 请实现此函数
    std::cout << "app_fin" << conn << std::endl;
}

/**
 * 当应用层想要重置连接(RES)时，会调用此函数
 * @param conn 连接对象
 */
void app_rst(ConnectionIdentifier &conn) {
    // TODO 请实现此函数
    std::cout << "app_rst" << conn << std::endl;
}

/**
 * 当收到TCP报文时，会调用此函数。
 * 正常情况下，你会对TCP报文，根据报文内容和连接的当前状态加以处理，然后调用0个~多个api文件中的函数
 * @param conn 连接对象
 * @param bytes TCP报文内容，是字节数组。（含TCP报头，不含IP报头）
 */
void tcp_rx(ConnectionIdentifier &conn, std::vector<uint8_t> &bytes) {
    // TODO 请实现此函数
    std::cout << "tcp_rx" << conn << bytes.data() << std::endl;
}
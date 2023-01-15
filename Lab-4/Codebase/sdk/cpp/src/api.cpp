/**
 * 这是SDK内置的代码，本文件是api.h中函数的实现。你只读api.h就够了。
 * 你可能不用改动此文件，但如果你确实需要的话（比如想加几个方法，或重载运算符之类），当然也可以改动。只要你清楚自己在做什么！
 * 助教评阅时，会使用你上传的版本。
 */
#include "api.h"

void sdk_event(ConnectionIdentifier &conn, std::vector<uint8_t> &bytes, uint32_t flags);

void app_connected(ConnectionIdentifier &conn) {
    std::vector<uint8_t> _;
    sdk_event(conn, _, 0x2);
}

void release_connection(ConnectionIdentifier &conn) {
    std::vector<uint8_t> _;
    sdk_event(conn, _, 0x80);
}

void app_recv(ConnectionIdentifier &conn, std::vector<uint8_t> &bytes) {
    sdk_event(conn, bytes, 0x0);
}

void app_peer_fin(ConnectionIdentifier &conn) {
    std::vector<uint8_t> _;
    sdk_event(conn, _, 0x1);
}

void app_peer_rst(ConnectionIdentifier &conn) {
    std::vector<uint8_t> _;
    sdk_event(conn, _, 0x4);
}

void tcp_tx(ConnectionIdentifier &conn, std::vector<uint8_t> &bytes) {
    sdk_event(conn, bytes, 0x40);
}

std::ostream &operator<<(std::ostream &out, ConnectionIdentifier &conn) {
    out << "(" << conn.src.ip << ":" << conn.src.port << " -> " << conn.dst.ip << ":" << conn.dst.port << ")";
    return out;
}

bool operator==(const ConnectionIdentifier &a, const ConnectionIdentifier &b) {
    return a.src.ip == b.src.ip && a.src.port == b.src.port && a.dst.ip == b.dst.ip && a.dst.port == b.dst.port;
}

/**
 * 这是SDK内置的代码，主要是与driver进行通信的逻辑。
 * 正常情况下，你应该也不需要阅读本文件的代码，只要读api文件，然后完成outgoing文件就好。
 * 此文件通常不用改动。但如果你有确切的理由，也可以自行改动，但请务必确保你清楚自己在做什么！
 * 助教评阅时，会使用你上传的版本。
 */
#include <iostream>
#include <vector>
#include "api.h"
#include "outgoing.h"
#include <sys/socket.h>
#include <sys/un.h>
#include <chrono>
#include <thread>
#include <csignal>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

int unix_sock = -1;

bool unix_socket_send(json &event) {
    auto data = json::to_bson(event);
    auto size = write(unix_sock, data.data(), data.size());
    if (size < 0) {
        perror("unix_sock send");
        return false;
    } else if (size < data.size()) {
        std::cerr << "WARNING: unix_sock write size < datagram.size()!" << std::endl;
        return false;
    }
    return true;
}

void sdk_event(ConnectionIdentifier &conn, std::vector<uint8_t> &bytes, uint32_t flags) {
    json event = {
            {"conn",  {
                              {"src", {
                                              {"ip", conn.src.ip},
                                              {"port", conn.src.port}
                                      }},
                              {"dst", {
                                              {"ip", conn.dst.ip},
                                              {"port", conn.dst.port}
                                      }}
                      }},
            {"flags", flags}
    };
    event["bytes"] = json::binary(bytes);

    if (!unix_socket_send(event)) {
        std::cerr << "unix_socket_send FAILED" << std::endl;
    }
}

bool unix_socket_recv(uint8_t buf[], size_t len) {
    auto size = read(unix_sock, buf, len);
    if (size < 0) {
        perror("unix_sock read");
        return false;
    }
    if (size == 1) { // 是保活报文
        tick();
        return true;
    }
    if (size >= len) {
        std::cerr << "WARNING: 收到了超过接收buffer大小({})的unix domain socket报文！该报文并未被完整接收！" << std::endl;
        return false;
    }
    json event = json::from_bson(buf, buf + size), conn_src = event["conn"]["src"], conn_dst = event["conn"]["dst"];
    ConnectionIdentifier conn{{conn_src["ip"].get<std::string>(), conn_src["port"].get<uint16_t>()},
                              {conn_dst["ip"].get<std::string>(), conn_dst["port"].get<uint16_t>()}};
    auto json_bytes = event["bytes"].get_binary();
    std::vector<uint8_t> bytes = std::vector(json_bytes.begin(), json_bytes.end());
    auto flags = event["flags"].get<uint32_t>();
    if (flags == 0x0) {
        app_send(conn, bytes);
    } else if (flags == 0x1) {
        app_fin(conn);
    } else if (flags == 0x2) {
        app_connect(conn);
    } else if (flags == 0x4) {
        app_rst(conn);
    } else if (flags == 0x40) {
        tcp_rx(conn, bytes);
    }
    return true;
}

int main() {
    remove("/tmp/network-exp4-sdk.socket");
    unix_sock = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (unix_sock < 0) {
        perror("socket");
        exit(1);
    }
    sockaddr_un local_addr{AF_UNIX, "/tmp/network-exp4-sdk.socket"}, peer_addr{AF_UNIX,
                                                                               "/tmp/network-exp4-driver.socket"};
    if (bind(unix_sock, reinterpret_cast<const sockaddr *>(&local_addr), sizeof(sockaddr_un))) {
        perror("bind");
        exit(1);
    }
    while (true) {
        if (connect(unix_sock, reinterpret_cast<const sockaddr *>(&peer_addr), sizeof(sockaddr_un))) {
            if (errno == 1) {
                std::cout << "等待服务端UnixSocket资源释放(约500ms)...(若持续出现此信息，请检查自己是否开着另一个SDK进程)"
                          << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
                continue;
            } else {
                perror("connect");
                exit(1);
            }
        }
        break;
    }
    // 向服务器发送初次连接的通告
    ConnectionIdentifier c{{"127.84.0.1", 8484},
                           {"",           0}};
    auto s = "network_exp4";
    auto v = std::vector<uint8_t>(s, s + strlen(s));
    sdk_event(c, v, 0xa0);
    uint8_t buf[500000];
    std::cout << "已启动！" << std::endl;
#pragma clang diagnostic push
#pragma ide diagnostic ignored "EndlessLoop"
    while (true) {
        if (!unix_socket_recv(buf, sizeof(buf))) {
            std::cerr << "unix_socket_recv FAILED" << std::endl;
        }
    }
#pragma clang diagnostic pop
}

/**
 * 这是SDK内置的代码，本文件是outgoing函数的声明，你应该去outgoing.cpp中对函数进行实现。
 * 函数相关的注释也全在outgoing.cpp里。
 * 此文件通常不用改动。但如果你有确切的理由，也可以自行改动，但请务必确保你清楚自己在做什么！
 * 助教评阅时，会使用你上传的版本。
 */
#ifndef NETWORK_EXP4_SDK_OUTGOING_H
#define NETWORK_EXP4_SDK_OUTGOING_H

#include "api.h"

void app_connect(ConnectionIdentifier &conn);

void app_send(ConnectionIdentifier &conn, std::vector<uint8_t> &bytes);

void app_fin(ConnectionIdentifier &conn);

void app_rst(ConnectionIdentifier &conn);

void tcp_rx(ConnectionIdentifier &conn, std::vector<uint8_t> &bytes);

void tick();

#endif //NETWORK_EXP4_SDK_OUTGOING_H

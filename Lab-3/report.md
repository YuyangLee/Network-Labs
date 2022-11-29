# 实验三 Socket 编程实现网络通信 实验报告

> 姓名：李宇飏
>
> 班级：自05
>
> 学号：2020011645

## SMTP

### 实验内容

1. 根据 SMTP 协议（RFC2821），补全无身份验证的 SMTP 程序；
2. 根据 SMTP 拓展协议（RFC2554），补全含有身份验证的 SMTP 程序。

### 实验过程

#### 补全 `SimpleSender.java`

补全代码请见 `CodeBase/SMTP/SimpleSender.java` 标注 `// DONE: x` 处。编译并运行，命令行输出见 `CodeBase/SMTP/SimpleSender.out`。

验证在邮箱 `liyuyang20@mails.tainghua.edu.cn` 收到了对应邮件：

![SimpleSender.Received](assets\SimpleSender.Received.png)

#### 补全 `AuthSender.java`

补全代码请见 `CodeBase/SMTP/AuthSender.java` 标注 `// DONE: x` 处。编译并运行，命令行输出见 `CodeBase/SMTP/AuthSender.out`，密码用 `*` 代替。

验证在邮箱 `i@aidenli.net` 收到了对应邮件：

![AuthSender.Received](assets\AuthSender.Received.png)

## TCP 聊天室

### 实验内容

1. 使用 Python 编写基于 Socket 的多人文字聊天室
2. 测试聊天室功能，包括：连接、收发消息、断连处理

### 实验过程

#### 编写聊天室

首先编写客户端、服务器类，由于二者具有一些相似的功能（比如创建接收/发送信息线程、记录 Log 等），首先编写父类 `ChatPeer`，然后派生 `ChatClient`, `ChatServer`。

服务器主要功能为：

1. 创建 `welcomeSocket`，监听客户端连接；
2. 维护 `clientPool`，将连接的客户端的客户端 accept 为 `serverSocket`；
3. 通过每个 `serverSocket` 监听并从客户端接收消息，并转发给其他所有连接；
4. 对于发送失败的 `serverSocket`，关闭与客户端的连接。

客户端主要功能为：

1. 创建 `clientSocket`，连接服务器；
2. 通过 `clientSocket` 监听并从服务器接收消息，并打印内容，同时显示发送方 IP、端口、时间；
3. 通过 `clientSocket` 向服务器发送消息；

此外，客户端、服务器均应当：

1. 充分记录 log，以 `INFO`, `DEBUG`, `ERROR` 等级别区分；
2. 妥当处理所有潜在的 exception 抛出；
3. 妥当地新建、维护和关闭线程，使前端非阻塞。

为了前端非阻塞，需要采用多线程/异步方法。为简洁记，本次采用 `threading.Thread` 通过多线程实现。具体地，

- `welcomeSocket` 及每个 `serverSocket` 单独新建线程，前者在服务器端程序结束时释放，后者在该 socket 连接失败后释放；
- `clientSocket` 单独新建线程，并在结束连接时释放；
- 客户端、服务端在发送每条消息时新建线程发送，在发送结束后释放。

此外，本次实验还是先了一些额外功能，包括但不限于：

1. 消息类型，目前支持：文本消息 `MSG`，控制消息 `CTL`（用于上线、下线通知）。
2. 用户上线、下线通知；
3. 用户端命令：如可以通过 `:q` 断开连接，通过 `::` 转义（如 `::q` 代表发送文本 ":q"）。

源码见 `CodeBase/TCP-Chat`。

#### 测试聊天室

若要测试聊天室，需要先安装依赖：

```shell
pip install logging
```

运行服务器：

```shell
python run.py --mode server --name Server --server_port PORT --log log/server.log
```

运行客户端：

```shell
python run.py --mode server --name Alice --server_addr ADDR --server_port PORT --log log/alice.log
```

其中，

- `ADDR`, `PORT` 为服务器对外开放服务的地址与端口（由 `welcomeSocket` 绑定）
- 服务端不需要指定 `server_addr`
- 而应当允许防火墙在 `server_port` 端口的 TCP 出入连接。

以

## 思考题与分析题


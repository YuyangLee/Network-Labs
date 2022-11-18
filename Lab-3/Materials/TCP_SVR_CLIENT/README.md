请注意，tcpserver.py和tcpclient.py中的代码，目前实现的是一个非常简单的TCP客户端和服务器通信功能：

1. 服务器阻塞在accept函数处，等待接受连接
2. 客户端向服务器发起连接，
3. 服务端接受连接，accept函数返回
4. 服务端代码向下运行，阻塞在recv函数处，等待接收信息
5. 客户端向服务器发送消息，服务端的recv函数返回，返回内容即为收到的消息
6. 服务器将收到的信息转为大写字母发给客户端
7. 服务器要求关闭连接
8. 客户端收到来自服务器的关闭连接请求，于是recv函数返回了一个长度为0的值
9. 客户端也关闭连接，然后客户端自身退出
10. 服务端完成一轮循环，进入下一轮，重新回到accept函数处等待接受连接。

这就意味着，客户端实际上只能一次性使用，发送一条信息并接收到服务器端的回复后会立即退出。  
更严重的是，当服务端阻塞在accept和recv函数处的时候，他是不能做其他任何事情的。  
假如，如果客户端连接之后一直没有向服务端发送消息，那么服务端不仅永远不会向这个客户端发送任何消息，也没办法做任何其他事情（例如接受其他用户的连接等）；
同样，假如服务端阻塞在accept处等待新客户端连进来，那么这期间服务端也无法接受任何已经连接上了的人的消息了。

你所实现的聊天程序不应是这样的，你所实现的聊天程序应当能够服务多个客户端。  
这意味着，你的程序不该是阻塞式的，不能是当你想要从用户1接收数据时就不能从用户2接收数据，而是应该保证你总能在很短的时间内响应每个用户发来的信息。  
为此，你很可能是要**在以下四种思路中选择一种实现**：
- **阻塞结合多线程**：实现难度★★☆☆
  - 你可以开启很多个线程，serverSocket一个线程，然后每接受到一个连接产生一个connectionSocket，就弄一个专门的线程去从中recv数据。
  - 为了实现多线程，你可能需要学习python的threading模块： https://docs.python.org/zh-cn/3/library/threading.html 
  - 事实上，tcpclient.py中用的就是这种模式。
- **超时模式**：实现难度★☆☆☆
  - 这种方式代码效率最低，因此真正的生产环境中很少有人这么用。但针对我们的实验还是够用的。
  - 将serverSocket和所有的connectionSocket设置为超时模式，然后用一个循环轮流从中recv。这样可以确保你的程序不会由于某个客户端一直不说话而就卡死了。
  - 设置超时后，可以确保每次recv的阻塞时间不会超过你设定的超时。如果recv函数在这段时间内没能收到任何数据，就会抛异常，你except住这个异常就可以了，从而避免一直死等下去。
  - 请参阅Python文档 https://docs.python.org/zh-cn/3/library/socket.html#socket-timeouts
- **poll模式**：实现难度★★★★
  - 这种方式代码效率最高，现实的生产环境中大多数都是用的这种，但是写起来比较复杂、需要对poll相关原理有一定的理解。
  - 原理简述：
    - 构造一个select.poll对象，然后把所有的socket对象都register进这个poll对象里。
    - 调用poll对象上的poll方法。此时poll对象会在后台监视所有注册过的socket，直到有任何被监视的socket变为可操作的状态（可以立即读到数据）再返回
    - poll方法返回的是一个数组，内含所有监视期间有数据到达的socket的相关信息。因此，我们迭代这个返回的数组，对对应的socket进行recv即可，此时recv函数必定不会阻塞。
  - 请参阅Python文档：https://docs.python.org/zh-cn/3/library/select.html#poll-objects
  - 或者，可以学习一些文章：例如
    - https://cloud.tencent.com/developer/article/1568723 
    - https://www.infoq.cn/article/26lpjzsp9echwgnic7lq
    - 但注意，这些文章讲的大多是epoll，epoll是一个仅在Linux下可用的方法。如果你并不使用Linux完成我们的作业，请改为使用poll。
- **asyncio**：实现难度★★☆☆，但需要关于asyncio的基础知识
  - 这种方式本质是Python底层帮助我们进行poll操作，因此代码效率较高的同时写起来难度不是特别大，但需要你了解asyncio的基础知识。
  - 此时，我们不应建立一般的socket，而是使用asyncio为我们提供的异步socket：见 https://docs.python.org/zh-cn/3/library/asyncio-stream.html 
  - 通过这种方式构造出的socket的reader，await reader.read时是挂起而非阻塞的，因此你可以比如说在主循环里await asyncio.wait(readFutures, return_when=asyncio.FIRST_COMPLETED)
  - 请自学关于asyncio的基础知识，网上有很多的学习资源。

其他的一些提示：
- 如何获取对端的地址、端口？请看https://docs.python.org/zh-cn/3/library/socket.html#socket.socket.getpeername 
- 如何获取当前的时间？
  - 建议使用datetime.datetime.now()，这个函数会返回一个datetime对象
  - datetime对象上有year、month、day、hour、minute、second等属性。
- encode和decode是什么意思？
  - 在Python中，有两个非常常见的类型：字符串str，和字节数组bytes。
  - 对于socket的相关方法如send、recv，参数和返回值都是bytes格式，而我们进行打印、字符串拼接等操作的的时候，往往是要用str格式。
  - 于是，encode和decode是它们之间的互转方法：
    - str.encode得到bytes
    - bytes.decode得到str



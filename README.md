## 实现 GTP 的 Python 封装

通过实现 Go Text Protocol 的 Python 封装重新学习 Python 的基础

- [x]  Python 启动 GTP 引擎（gnugo）
    - [x]  Python 通过 socket 连接到本地运行的 gnugo `gnugo --mode gtp --gtp-listen 127.0.0.1:20230`
    - [x]  Python 作为服务端，而 gnugo 作为客户端连接 `gnugo --mode gtp --gtp-connect 127.0.0.1:20230`
    - [x]  不使用 Socket 直接使用 gnugo 的 cli 界面 `gnugo --mode gtp` 更加简洁明了
    - [x]  参数控制棋盘大小
- [x]  两个 GTP 引擎通过封装进行对局
    - [x]  两个 gnugo 引擎通过 tcp socket 连接到服务端
    - [x]  依次向每个引擎发送 genmove 命令，实现引擎间的对局
        - [x]  至少三个线程，一个线程处理数据，两个线程代表连接引擎，分别为 A 和 B
            - [x]  不需要多线程，因为两个引擎实际上是顺序执行的，并不存在同步执行的情况
        - [x]  初始时上次走棋为 None
        - [x]  A 根据上次走棋情况，再次走棋，然后 genmove b 走一步黑棋，取得落点坐标，更新上次走棋情况
        - [x]  B 根据上次走棋情况，再次走棋，然后 genmove w 走一步白棋，取得落点坐标，更新上次走棋情况
        - [x]  根据走棋情况更新棋盘
    - [x]  输出对局过程
- [ ]  建立网站实现对局可视化
- [ ]  可以通过网站和引擎进行对局
- [ ]  通过数据库保存对局
- [ ]  实现 AI 复盘，复盘过程中可继续对局

Python

- subprocess
- socket
- argparse
- logging
- 项目结构 https://docs.python-guide.org/writing/structure/#makefile

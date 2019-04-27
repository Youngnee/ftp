"""
ftp_server.py


"""

import os, sys
from socket import *
import signal
import time

# 定义全局变量
HOST = "0.0.0.0"
PORT = 9009
ADDR = (HOST,PORT)
FILE_PATH = "/home/tarena/test/" # 文件路径

# 服务端功能类
class FtpServer(object):
    def __init__(self,connfd):
        self.connfd = connfd

    def do_list(self):
        # 获取文件列表
        file_list = os.listdir(FILE_PATH)
        if not file_list:
            self.connfd.send("文件库为空".encode())
            return
        else:
            self.connfd.send(b"OK")
            time.sleep(0.1)

        files = ""
        for file in file_list:
            if file[0] != "." and os.path.isfile(
                FILE_PATH + file):
                files += file + "#"
        self.connfd.send(files.encode())

    def do_get(self,filename):
        try:
            fd = open(FILE_PATH + filename,"rb")
        except IOError:
            self.connfd.send("文件不存在".encode())
            return
        else:
            self.connfd.send(b"OK")
            time.sleep(0.1)
        
        while True:
            data = fd.read(1024)
            if not data:
                time.sleep(0.1)
                self.connfd.send(b"##")
                break
            self.connfd.send(data)
        fd.close()

    def do_put(self,filename):
        # 判断是否存在文件
        if os.path.exists(FILE_PATH + filename):
            self.connfd.send("该文件已存在".encode())
            return
        fd = open(FILE_PATH + filename,"wb")
        self.connfd.send(b"OK")
        while True:
            data = self.connfd.recv(1024)
            if data == b"##":
                break
            fd.write(data)
        fd.close()



    # def do_put(self,filename):
    #     data = self.connfd.send(b"OK")
    #     time.sleep(0.1)
    #     fd = open(FILE_PATH + "c_" + filename,"wb")
    #     while True:
    #         data = self.connfd.recv(1024)
    #         if data == b"##":
    #             break
    #         fd.write(data)
    #     fd.close()




def do_request(connfd):
    ftp = FtpServer(connfd)
    while True:
        data = connfd.recv(2048).decode()
        if not data or data[0] == "Q":
            connfd.close()
            return
        elif data[0] == "L":
            ftp.do_list()
        elif data[0] == "G":
            filename = data.split(" ")[-1]
            ftp.do_get(filename)
        elif data[0] == "P":
            filename = data.split(" ")[-1]
            ftp.do_put(filename)
        

def sockfd():
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)
    # 处理僵尸进程
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    print("Listen the port 9009...")
    return s

def conn(s):
    # 循环等待客户端连接
    while True:
        try:
            c,addr = s.accept()
        except KeyboardInterrupt as e:
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue
        print("Connect From:",addr)

        # 创建子进程
        pid = os.fork()

        if pid == 0:
            s.close()
            do_request(c)# 处理客户端请求
            os._exit(0)
        else:
            c.close()

def main():
    s = sockfd()
    conn(s)


if __name__ == "__main__":
    main()


"""
ftp_client.py

"""
import os, sys
from socket import *
import time

# FILE_PATH = "/home/tarena/Yang01/python_network/day08/"
# 服务器地址
ADDR = ("176.140.7.75",9009)

class FtpClient(object):
    def __init__(self,sockfd):
        self.sockfd = sockfd
    
    def do_list(self):
        self.sockfd.send("L".encode())# 发送请求
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            files = self.sockfd.recv(4096).decode()
            for file in files.split("#"):
                print(file)
        else:
            # 无法完成操作
            print(data)

    def do_quit(self):
        self.sockfd.send(b"Q")
        self.sockfd.close()
        sys.exit("谢谢使用")

    def do_get(self,filename):
        self.sockfd.send(("G "+filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            fd = open(filename,"wb")
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":
                    break
                fd.write(data)
            fd.close()        
        else:
            print(data)

    def do_put(self,filename):
        try:
            fd = open(filename,"rb")
        except IOError:
            print("文件不存在,请检查")
            return
        # 获取文件名
        filename = filename.split("/")[-1]
        self.sockfd.send(("P " + filename).encode())
        data = self.sockfd.recv(1024).decode()
        if data == "OK":
            while True:
                data = fd.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sockfd.send(b"##")
                    break
                self.sockfd.send(data)
            fd.close()
        else:
            print(data)

    # def do_put(self, filename):
    #     try:
    #        fd = open(FILE_PATH + filename,"rb") 
    #     except IOError:
    #         print("文件不存在,请检查")
    #         return

    #     self.sockfd.send(("S "+filename).encode())
    #     data = self.sockfd.recv(128).decode()
    
    #     if data == "OK":
    #         while True:
    #             data = fd.read(1024)
    #             if not data:
    #                 time.sleep(0.1)
    #                 self.sockfd.send(b"##")
    #                 break
    #             self.sockfd.send(data)
    #         fd.close()
    #     else:
    #         print(data)




def print_menu():
        print("\n========命令选项========")
        print("***      list        ***")
        print("***    get  file     ***")
        print("***    put  file     ***")
        print("***      quit        ***")
        print("========================")


def main():
    sockfd = socket()
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print(e)
        return
    
    # 创建一个对象,调用功能函数
    ftp = FtpClient(sockfd)
    
    while True:
        print_menu()
        try:
            cmd = input("输入命令>>")
        except KeyboardInterrupt:
            print("退出客户端")
            sockfd.close()
            return
        
        if cmd.strip() == "list":
            ftp.do_list()
        elif cmd.strip() == "quit":
            ftp.do_quit()
        elif cmd[:3] == "get":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_get(filename)
        elif cmd[:3] == "put":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_put(filename)
        else:
            print("请输入正确命令!")


if __name__ == "__main__":
    main()
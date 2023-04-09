import os
import time
from socket import *


class Handle:
    def __init__(self, addr: tuple):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.addr = addr
        self.size = 1024 * 1024 * 4
        self.b_status = (b"SUCCESS", b"FAIL", b"NOT FIND", b"CANCEL", b"REFUSED", b"NOT FOLDER")
        self.status = {
            "SUCCESS": "传输成功",
            "FAIL": "传输失败",
            "NOT FIND": "文件不存在",
            "CANCEL": "取消操作",
            "REFUSED": "连接服务器被拒绝",
            "NOT FOLDER": "非文件夹"
        }
        self.exec = {
            "1": self.__do_list,
            "2": self.__do_get,
            "3": self.__do_put
        }
        self.__connect()

    def __connect(self):
        try:
            self.socket.connect(self.addr)
        except ConnectionRefusedError:
            print(self.status["REFUSED"])

    def __do_list(self):
        self.__send("LIST")
        self.__recv()
        while True:
            list_select = input("请使用相对路径选择文件夹\n(输入0退出)选择：")
            if list_select == "0":
                print(self.status["CANCEL"])
                return
            self.__send(f"SELECT {list_select}")
            self.__recv()

    def __do_get(self):
        path = input("(输入0退出)下载文件：")
        if path == "0":
            print(self.status["CANCEL"])
            return
        self.__send(f"GET {path}")
        with open(path, "ab") as fa:
            while True:
                data = self.socket.recv(self.size)
                if data in self.b_status:
                    print(self.status[data.decode()])
                    break
                fa.write(data)

    def __do_put(self):
        try:
            path = input("(输入0退出)上传文件：")
            if path == "0":
                print(self.status["CANCEL"])
                return
            if not os.path.exists(path):
                print(self.status["NOT FIND"])
                return
            self.__send(f"PUT {path}")
            with open(path, "rb") as fr:
                while True:
                    bytes_ = fr.read(self.size)
                    if not bytes_:
                        break
                    self.socket.send(bytes_)
        except Exception as e:
            time.sleep(0.05)
            self.socket.send(b"FAIL")
            print(self.status["FAIL"], e)
        else:
            time.sleep(0.05)
            self.socket.send(b"SUCCESS")
            print(self.status["SUCCESS"])

    def stop(self):
        self.__send("QUIT")
        self.socket.close()

    def __send(self, msg: str):
        self.socket.send(msg.encode())

    def __recv(self):
        msg = self.socket.recv(self.size)
        print(msg.decode())


class FTPView:
    def __init__(self):
        self.handle = Handle(("127.0.0.1", 8888))
        self.menu = "FTP服务客户端" \
                    "\n=====================================" \
                    "\n1.查看文件库   2.下载文件   3.上传文件" \
                    "\n注：输入quit或exit或0退出程序" \
                    "\n====================================="

    def __select(self):
        while True:
            try:
                msg = input(">>> ")
                if not msg or msg in ("quit", "exit", "0"):
                    self.handle.stop()
                    break
                self.handle.exec[msg]()
            except KeyboardInterrupt:
                print("客户端退出")
            except KeyError:
                print("无效指令")

    def show(self):
        print(self.menu)
        self.__select()


if __name__ == '__main__':
    view = FTPView()
    view.show()

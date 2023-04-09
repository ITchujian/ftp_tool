"""
    FTP Server
"""
import sys
import os
import time
from threading import Thread
from socket import *


class Handle(Thread):
    def __init__(self, conn: socket, address: tuple, path: str):
        self.conn, self.address, self.path = conn, address, path
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
        super().__init__()

    def run(self):
        while True:
            request = self.conn.recv(self.size)
            request = request.decode().split(" ", 1)
            if request[0] == "LIST":
                self.do_list()
            elif request[0] == "SELECT" and len(request) == 2:
                self.do_select(request[1])
            elif request[0] == "GET" and len(request) == 2:
                self.do_get(request[1])
            elif request[0] == "PUT" and len(request) == 2:
                self.do_put(request[1])
            elif request[0] == "QUIT":
                self.quit()
                break

    def quit(self):
        self.conn.close()
        print(f"客户端 {self.address} 断开连接")

    def do_list(self, path: str = None):
        source_path = self.path
        self.path = path or self.path
        print(f"客户端 {self.address} 查询{self.path}的文件")
        scan = os.scandir(self.path)
        files, folders = [], []
        for file in scan:
            if file.is_file():
                files.append(file.name)
            else:
                folders.append(file.name)
        files, folders = sorted(files), sorted(folders)
        all_ = f"文件：{'  '.join(files) if len(files) else '空'}\n文件夹：{'  '.join(folders) if len(folders) else '空'}\n"
        self.conn.send(str(all_).encode())
        self.path = source_path

    def do_select(self, folder):
        folder = os.path.join(self.path, folder)
        if not os.path.isdir(folder):
            self.conn.send(b"NOT FOLDER")
            return
        self.do_list(folder)

    def do_get(self, path):
        try:
            print(f"客户端 {self.address} 申请下载文件{path}")
            file_path = os.path.join(self.path, path)
            if not os.path.exists(file_path):
                print(f"客户端 {self.address} 所下载文件{path}不存在")
                self.conn.send(b"NOT FIND")
                return
            with open(file_path, "rb") as fr:
                while True:
                    bytes_ = fr.read(self.size)
                    if not bytes_:
                        break
                    self.conn.send(bytes_)
        except Exception as e:
            time.sleep(0.05)
            self.conn.send(b"FAIL")
            print(f"客户端 {self.address} 下载文件{path}失败，原因如下:\n{e}")
        else:
            time.sleep(0.05)
            self.conn.send(b"SUCCESS")
            print(f"客户端 {self.address} 下载文件{path}成功")

    def do_put(self, path):
        print(f"客户端 {self.address} 申请上传文件{path}")
        file_path = os.path.join(self.path, path)
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "ab") as fa:
            while True:
                data = self.conn.recv(self.size)
                if data in self.b_status:
                    print(f"客户端 {self.address} 上传文件", self.status[data.decode()])
                    break
                fa.write(data)


class FTPServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8888, count: int = 5):
        self.host, self.port, self.count = host, port, count
        self.server_addr = (self.host, self.port)
        self.sock = socket(AF_INET, SOCK_STREAM)

    def __create(self):
        self.sock.bind(self.server_addr)
        print("服务绑定地址中......")
        self.sock.listen(self.count)
        print(f"服务创建中，监听等待队列容量：{self.count}")

    def run(self, run_handle: Handle = None):
        run_handle = run_handle or Handle
        self.__create()
        while True:
            print("服务端等待连接中......")
            try:
                conn, addr = self.sock.accept()
                print(f"客户端 {addr} 建立连接")
            except KeyboardInterrupt:
                self.sock.close()
                sys.exit("服务结束")
            handle = run_handle(conn, addr, "/home/ronan/FTP")
            handle.start()


if __name__ == '__main__':
    server = FTPServer()
    server.run()

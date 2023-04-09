# FTP工具-固定文件库版

基于TCP协议使用Python开发的FTP上传下载工具,比较简陋

其中服务端与客户端之间各设计得有 操作请求和完成响应的通信协议，如"LIST" "GET [filename]"等等

请使用相对路径，测试平台为`Linux Mint`

注意文件系统权限问题

# 菜单命令

- 1 当前路径下的所有文件以及文件夹
- 2 将所在路径下的服务器文件下载到本地文件，同名文件可被创建
- 3 将本地文件上传到所在服务器的路径下，同名服务器文件可被创建
- quit 退出客户端
- exit 同上
- 0 同上

# 使用方法

1. 将ftp_server_new挂在服务端，在该python文件中，找到FTPServer类，修改run方法中的run_handle的路径（绝对路径），也就是文件库所在
2. 在服务端终端运行 `python3 ftp_server_new.py`
3. 将ftp_clien_newt中FTPView类中的实例化Handle对象的ip地址更换成服务端的ip地址
4. 在pycharm或者客户端终端运行 `python3 ftp_clien_newt.py`

如若出现端口被占用，更换端口即可

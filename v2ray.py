#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import commands


def open_port(port):
    cmd = [
        "iptables -I INPUT -m state --state NEW -m tcp -p tcp --dport $1 -j ACCEPT",
        "iptables -I INPUT -m state --state NEW -m udp -p udp --dport $1 -j ACCEPT",
        "ip6tables -I INPUT -m state --state NEW -m tcp -p tcp --dport $1 -j ACCEPT",
        "ip6tables -I INPUT -m state --state NEW -m udp -p udp --dport $1 -j ACCEPT"
    ]

    for x in cmd:
        x = x.replace("$1", str(port))
        commands.getoutput(x)


def start():
    os.system("""supervisorctl start v2ray.fun""")


def stop():
    os.system("""supervisorctl stop v2ray.fun""")


def write(data):
    with open("/usr/local/V2ray.Fun/panel.config", "w") as f:
        json.dump(data, f, indent=2)


if __name__ == '__main__':
    with open("/usr/local/V2ray.Fun/panel.config") as f:
        data = json.load(f)

    print("欢迎使用 V2ray.Fun 面板 ---- By 雨落无声\n")
    print("当前面板用户名：" + str(data['username']))
    print("当前面板密码：" + str(data['password']))
    print("当前面板监听端口：" + str(data['port']))
    print("请输入数字选择功能：\n")
    print("1. 启动面板")
    print("2. 停止面板")
    print("3. 重启面板")
    print("4. 设置面板用户名和密码")
    print("5. 设置面板端口")
    choice = str(input("\n请选择："))

    if choice == "1":
        start()
        open_port(data['port'])
        print("启动成功!")

    elif choice == "2":
        stop()
        print("停止成功！")

    elif choice == "3":
        stop()
        start()
        open_port(data['port'])
        print("重启成功!")
    elif choice == "4":
        new_username = str(raw_input("请输入新的用户名："))
        new_password = str(raw_input("请输入新的密码："))
        data['username'] = new_username
        data['password'] = new_password
        write(data)
        stop()
        start()
        print("用户名密码设置成功！")
    elif choice == "5":
        new_port = input("请输入新的面板端口：")
        data['port'] = int(new_port)
        write(data)
        stop()
        start()
        open_port(data['port'])
        print("面板端口已修改！")

#! /usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import requests


# def base64_decode(base64_encode_str):
#    """ 利用 base64.urlsafe_b64decode 对字符串解码 python2.7下会有问题"""
#    if base64_encode_str:
#        need_padding = len(base64_encode_str) % 4
#        if need_padding != 0:
#            missing_padding = 4 - need_padding
#            base64_encode_str += '=' * missing_padding
#        return base64.urlsafe_b64decode(base64_encode_str).decode('utf-8')
#    return base64_encode_str
#    return base64.b64decode(base64_encode_str)


def parse(vmessUrl):
    """解析vmess链接
    :args:
        vmessUrl: vmess 链接
    :return:
        vmess_result: vmess链接解析结果,json格式
    """
    vmess_json = json.loads(base64.b64decode(vmessUrl[8:]))
    return vmess_json


def parseSubscribtxt(SubscribTxt):
    """解码订阅的base64编码字符串
    :args:
        SubscribTxt: 从订阅文件中读取的经过编码的字符串
    :return:
        订阅的vmess链接列表

    """
    decodeTxt = base64.b64decode(SubscribTxt)
    subscribList = decodeTxt.splitlines()
    return subscribList


def get_vmess_json(subscrib_url):
    r = requests.get(subscrib_url)
    s = r.text
    vmess_url_list = parseSubscribtxt(s)
    vmess_json_list = []
    for line in vmess_url_list:
        if line:
            vmess_json = parse(line)
#            if vmess_json['class'] == 3:
            vmess_json_list.append(vmess_json)
    print(vmess_json_list)
    return vmess_json_list


def let_update_subscribe(subscribe_url):
    #   更新订阅数据
    vmess_json_list = get_vmess_json(subscribe_url)
#    with open("subscribe.list") as f:
    subscrib_list = json.loads("""{"active":0,"max":0,"list":[]}""")

    i = 0
    for vmess in vmess_json_list:
        config_from_subscribe = json.loads("""
        {
        "tls": "",
        "status": "",
        "encrypt": "",
        "uuid": "",
        "domain_ip": "",
        "secret": "",
        "mux": "",
        "port": "",
        "host": "",
        "routing": "",
        "remarks": "",
        "protocol": "",
        "trans": "",
        "wspath": "",
        "alterId": ""
        }
        """)
        if vmess['tls'] == "tls":
            config_from_subscribe["tls"] = "on"
        config_from_subscribe["status"] = "on"
        config_from_subscribe["encrypt"] = 'auto'
        config_from_subscribe["uuid"] = vmess['id']
        config_from_subscribe["domain_ip"] = vmess['add']
        config_from_subscribe["mux"] = 'on'
        config_from_subscribe["wspath"] = vmess['path']
        config_from_subscribe["secret"] = ""
        config_from_subscribe["routing"] = 'whitelist'
        config_from_subscribe["remarks"] = vmess['ps']
        config_from_subscribe["protocol"] = 'vmess'
        if vmess['net'] == "ws":
            config_from_subscribe["trans"] = "websocket"
        elif vmess['net'] == "tcp":
            config_from_subscribe["trans"] = "tcp"
        else:
            config_from_subscribe["trans"] = "mkcp"
        config_from_subscribe["host"] = vmess['host']
        config_from_subscribe["alterId"] = str(vmess['aid'])
        config_from_subscribe["port"] = str(vmess['port'])
#        print(config_from_subscribe)
        subscrib_list["list"].append(config_from_subscribe)
        i = i + 1
    subscrib_list["max"] = i - 1
    subscrib_list["active"] = 0
#    print(subscrib_list)
#    commands.getoutput('mv subscribe.list subscribe.list.bak')
    with open("subscribe.list", "w") as f:
        f.write(json.dumps(subscrib_list, indent=2))


if __name__ == "__main__":

    with open("panel.config") as panel_config:
        panel = json.load(panel_config)
    print(panel['subscribe_url'])
    let_update_subscribe(panel['subscribe_url'])

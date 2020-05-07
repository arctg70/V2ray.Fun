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
            if vmess_json['class'] == 3:
                vmess_json_list.append(vmess_json)
    print(vmess_json_list)
    return vmess_json_list


def let_update_subscribe(subscribe_url):
    #   更新订阅数据
    vmess_json_list = get_vmess_json(subscribe_url)
    with open("subscribe.list") as f:
        subscrib_list = json.load(f)
    i = 0
    for vmess in vmess_json_list:
        if vmess['tls'] == "tls":
            subscrib_list['list'][i]["tls"] = "on"
        subscrib_list["list"][i]["status"] = "on"
        subscrib_list["list"][i]["encrypt"] = 'auto'
        subscrib_list["list"][i]["uuid"] = vmess['id']
        subscrib_list["list"][i]["domain_ip"] = vmess['add']
        subscrib_list["list"][i]["mux"] = 'on'
        subscrib_list["list"][i]["wspath"] = vmess['path']
        #   subscrib_list['list'][i]["secret"]="44369f5382d51e6fcc4c254d1fc43820"
        #   subscrib_list['list'][i]["routing"] = 'whitelist'
        subscrib_list["list"][i]["remarks"] = vmess['add']
        if vmess['net'] == "ws":
            subscrib_list["list"][i]["trans"] = "websocket"
        elif vmess['net'] == "tcp":
            subscrib_list["list"][i]["trans"] = "tcp"
        else:
            subscrib_list["list"][i]["trans"] = "mkcp"
        subscrib_list["list"][i]["host"] = vmess['host']
        subscrib_list["list"][i]["alterId"] = str(vmess['aid'])
        subscrib_list["list"][i]["port"] = str(vmess['port'])
        i = i + 1
    print(subscrib_list)
#    commands.getoutput('mv subscribe.list subscribe.list.bak')
    with open("subscribe.list", "w") as f:
        f.write(json.dumps(subscrib_list, indent=2))


if __name__ == "__main__":

    with open("panel.config") as panel_config:
        panel = json.load(panel_config)
    print(panel['subscribe_url'])
    let_update_subscribe(panel['subscribe_url'])

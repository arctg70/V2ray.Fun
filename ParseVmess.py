#! /usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import requests


def base64_decode(base64_encode_str):
    """ 利用 base64.urlsafe_b64decode 对字符串解码 """
    if base64_encode_str:
        need_padding = len(base64_encode_str) % 4
        if need_padding != 0:
            missing_padding = 4 - need_padding
            base64_encode_str += '=' * missing_padding
        return base64.urlsafe_b64decode(base64_encode_str).decode('utf-8')
    return base64_encode_str


def parse(vmessUrl):
    """解析vmess链接
    :args:
        vmessUrl: vmess 链接
    :return:
        vmess_result: vmess链接解析结果,json格式
    """
    vmess_json = json.loads(base64_decode(vmessUrl[8:]))
    return vmess_json


def parseSubscribtxt(SubscribTxt):
    """解码订阅的base64编码字符串
    :args:
        SubscribTxt: 从订阅文件中读取的经过编码的字符串
    :return:
        订阅的vmess链接列表

    """
    decodeTxt = base64_decode(SubscribTxt)
    subscribList = decodeTxt.splitlines()
    return subscribList


if __name__ == "__main__":
    #    with open("node1.txt") as f:
    #        s = f.read()
    r = requests.get('subscrib_url_from_airport')
    s = r.text
    vlist = parseSubscribtxt(s)
    for line in vlist:
        if line:
            vmess = parse(line)
            print(vmess)


#    with open("nodelist.txt",'w') as f:
#        f.write(s)
#    with open("nodelist.txt") as f:
#        s=base64_decode(f.readline()[8:])
#
#        print(s)

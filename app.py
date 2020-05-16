#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os

from flask_apscheduler import APScheduler

from flask import Flask, render_template, request
from flask_basicauth import BasicAuth

from config_generator import *  # noqa
from ParseVmess import *

os.chdir("/usr/local/V2ray.Fun")

with open("panel.config") as f:
    panel_config = json.load(f)


class Config(object):
    SCHEDULER_API_ENABLED = True


UpdateScheduler = APScheduler()


@UpdateScheduler.task('interval', id='subscribeUpdate', days=7)
def subscribeUpdate():
    update_subscribe()


@UpdateScheduler.task('interval', id='v2rayUpdate', weeks=4)
def v2rayUpdate():
    update_v2ray()


app = Flask(__name__, static_url_path='/static')

app.config['BASIC_AUTH_USERNAME'] = panel_config['username']
app.config['BASIC_AUTH_PASSWORD'] = panel_config['password']
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)

app.config.from_object(Config())
UpdateScheduler.init_app(app)

UpdateScheduler.start()
UpdateScheduler.pause_job('subscribeUpdate')
UpdateScheduler.pause_job('v2rayUpdate')

if panel_config["auto_update_subscribe"] == "open":
    update_subscribe()
    UpdateScheduler.resume_job('subscribeUpdate')

if panel_config["auto_update_v2ray"] == "open":
    update_v2ray()
    UpdateScheduler.resume_job('v2rayUpdate')


def change_config(config, value):
    with open("config.list") as f:
        old_json_list = json.load(f)
        active = old_json_list['active']
        old_json = old_json_list['list'][active]
    old_json_list['list'][active] = old_json

    old_json[str(config)] = str(value)

    with open("config.list", "w") as f:
        json.dump(old_json_list, f, indent=2)


def change_panel(config, value):
    with open("panel.config") as panel_config:
        panel = json.load(panel_config)
    panel[str(config)] = str(value)
    with open("panel.config", "w") as f:
        json.dump(panel, f, indent=2)


def change_node(value):
    with open("config.list") as f:
        old_json_list = json.load(f)

    old_json_list['active'] = value

    with open("config.list", "w") as f:
        json.dump(old_json_list, f, indent=2)


def change_subscribe_node(value):
    with open("subscribe.list") as f:
        old_json_list = json.load(f)

    old_json_list['active'] = value

    with open("subscribe.list", "w") as f:
        json.dump(old_json_list, f, indent=2)


def update_subscribe():
    #   更新订阅数据
    with open("panel.config") as panel_config:
        panel = json.load(panel_config)
#    print(panel['subscribe_url'])
    if let_update_subscribe(panel['subscribe_url']):
        change_panel("subscribe_log", "success")

#    commands.getoutput('mv subscribe.list subscribe.list.bak')
#    with open("subscrib.list", "w") as f:
#        json.dump(subscrib_list, f, indent=2)
#

    """ cmd = "bash subscribe.sh " + \
        panel["subscribe_url"] + " " + panel["subscribe_code"]
    output = commands.getoutput(cmd)
    success_wget = output.find('saved')
    success_unzip = output.find('inflating')
    if success_wget != -1 and success_unzip != -1:
        change_panel("subscribe_log", "success")
    else:
        change_panel("subscribe_log", "failure")
        commands.getoutput('mv subscribe.list.bak subscribe.list')
    """


def update_v2ray():
    cmd_get_new_ver = """curl -s https://api.github.com/repos/v2ray/v2ray-core/releases/latest --connect-timeout 10| grep 'tag_name' | cut -d '"' -f4"""
    new_ver = commands.getoutput(cmd_get_new_ver)

    change_panel("v2ray_new_ver", str(new_ver))
    with open("panel.config") as panel_config:
        json_panel = json.load(panel_config)
    if json_panel["v2ray_new_ver"] != json_panel["v2ray_current_ver"]:
        update_log = commands.getoutput("bash updateV2ray.sh")
        success_update = update_log.find('installed')
        if success_update != -1:
            cmd_get_current_ver = """echo `/usr/bin/v2ray/v2ray -version 2>/dev/null` | head -n 1 | cut -d " " -f2"""
            current_ver = 'v' + commands.getoutput(cmd_get_current_ver)
            change_panel("v2ray_current_ver", str(current_ver))
            change_panel("update_log", "success")
        else:
            change_panel("update_log", "failure")


def change_domain_to_remark(value):
    with open("config.list") as f:
        old_json_list = json.load(f)
        active = old_json_list['active']
        old_json = old_json_list['list'][active]
    if old_json['remarks'] == 'bank':
        old_json['remarks'] = str(value)

    old_json_list['list'][active] = old_json

    with open("config.list", "w") as f:
        json.dump(old_json_list, f, indent=2)


def get_status():
    cmd = """ps -ef | grep "v2ray" | grep -v grep | awk '{print $2}'"""
    output = commands.getoutput(cmd)
    if output == "":
        return "off"
    else:
        return "on"


@app.route('/start_service')
def start_service():
    cmd = "service v2ray start"
    commands.getoutput(cmd)
    change_config("status", "on")
    return "OK"


@app.route('/stop_service')
def stop_service():
    cmd = "service v2ray stop"
    commands.getoutput(cmd)
    change_config("status", "off")
    return "OK"


@app.route('/restart_service')
def restart_service():
    cmd = "service v2ray restart"
    commands.getoutput(cmd)
    change_config("status", "on")
    return "OK"


@app.route('/open_auto_update_subscribe')
def open_auto_update_subscribe():
    change_panel("auto_update_subscribe", "open")
    UpdateScheduler.resume_job('subscribeUpdate')
    return "OK"


@app.route('/stop_auto_update_subscribe')
def stop_auto_update_subscribe():
    change_panel("auto_update_subscribe", "stop")
    UpdateScheduler.pause_job('subscribeUpdate')

    return "OK"


@app.route('/open_auto_update_v2ray')
def open_auto_update_v2ray():
    change_panel("auto_update_v2ray", "open")
    UpdateScheduler.resume_job('v2rayUpdate')
    return "OK"


@app.route('/stop_auto_update_v2ray')
def stop_auto_update_v2ray():
    change_panel("auto_update_v2ray", "stop")
    UpdateScheduler.pause_job('v2rayUpdate')

    return "OK"


@app.route('/set_protocol', methods=['GET', 'POST'])
def set_protocol():
    items = request.args.to_dict()
    if items['protocol'] == "1":
        change_config('protocol', 'vmess')
    elif items['protocol'] == "2":
        change_config('protocol', 'mtproto')
    # gen_server()
    gen_client()
    return "OK"


@app.route('/set_secret', methods=['GET', 'POST'])
def set_secret():
    items = request.args.to_dict()
    change_config('secret', items['secret'])
    return "OK"


@app.route('/set_uuid', methods=['GET', 'POST'])
def set_uuid():
    items = request.args.to_dict()
    change_config("uuid", items['setuuid'])
    # gen_server()
    gen_client()
    restart_service()
    return "OK"


@app.route('/set_tls', methods=['GET', 'POST'])
def set_tls():
    items = request.args.to_dict()
    if (items['action'] == "off"):
        change_config('tls', 'off')
    else:
        change_config("tls", "on")
    # gen_server()
    gen_client()
    restart_service()

    return "OK"


@app.route('/set_mux', methods=['GET', 'POST'])
def set_mux():
    items = request.args.to_dict()
    change_config("mux", items['action'])
    gen_client()
    return "OK"


@app.route('/set_wspath', methods=['GET', 'POST'])
def set_wspath():
    items = request.args.to_dict()
    change_config("wspath", items['setwspath'])
    # gen_server()
    gen_client()
    restart_service()
    return "OK"


@app.route('/set_domain_ip', methods=['GET', 'POST'])
def set_domain_ip():
    items = request.args.to_dict()
    change_config("domain_ip", items['setdomainip'])
    change_domain_to_remark(items['setdomainip'])
    # gen_server()
    gen_client()
    restart_service()
    return "OK"


@app.route('/set_remark', methods=['GET', 'POST'])
def set_remark():
    items = request.args.to_dict()
    change_config("remarks", items['setremark'])
    # gen_server()
    gen_client()
    restart_service()
    return "OK"


@app.route('/set_host', methods=['GET', 'POST'])
def set_host():
    items = request.args.to_dict()
    change_config("host", items['sethost'])
    # gen_server()
    gen_client()
    restart_service()
    return "OK"


@app.route('/set_alterId', methods=['GET', 'POST'])
def set_alterId():
    items = request.args.to_dict()
    alterId = items['setalterId']
    print(alterId)
    change_config("alterId", items['setalterId'])
    # gen_server()
    gen_client()
    restart_service()
    return "OK"


@app.route('/set_port', methods=['GET', 'POST'])
def set_port():
    items = request.args.to_dict()
    change_config("port", items['setport'])
    # gen_server()
    gen_client()
    restart_service()
    return "OK"


@app.route('/set_encrypt', methods=['GET', 'POST'])
def set_encrypt():
    items = request.args.to_dict()
    encrypt = str(items['encrypt'])
    if encrypt == "1":
        change_config("encrypt", "auto")
    elif encrypt == "2":
        change_config("encrypt", "aes-128-cfb")
    elif encrypt == "3":
        change_config("encrypt", "aes-128-gcm")
    elif encrypt == "4":
        change_config("encrypt", "chacha20-poly1305")
    else:
        change_config("encrypt", "none")
    # gen_server()
    gen_client()
    restart_service()

    return "OK"


@app.route('/set_node', methods=['GET', 'POST'])
def set_node():
    items = request.args.to_dict()
    node = str(items['node'])
    if node == "1":
        change_node(0)
    elif node == "2":
        change_node(1)
    elif node == "3":
        change_node(2)
    elif node == "4":
        change_node(3)
    elif node == "5":
        change_node(4)
    elif node == "6":
        change_node(5)
    elif node == "7":
        change_node(6)
    elif node == "8":
        change_node(7)
    elif node == "9":
        change_node(8)
    elif node == "10":
        change_node(9)
    else:
        change_node(0)
    change_panel("config_source", "config.list")
    # gen_server()
    gen_client()
    restart_service()

    return "OK"


@app.route('/set_routing', methods=['GET', 'POST'])
def set_routing():
    items = request.args.to_dict()
    routing = str(items['routing'])
    if routing == "1":
        change_panel("routing", "global")
    elif routing == "2":
        change_panel("routing", "whitelist")
    elif routing == "3":
        change_panel("routing", "direct")
    else:
        change_panel("routing", "direct")
    # gen_server()
    gen_client()
    restart_service()

    return "OK"


@app.route('/set_subscribe', methods=['GET', 'POST'])
def set_subscribe():
    items = request.args.to_dict()
    change_panel("subscribe_url", str(items['url']))
    change_panel("subscribe_code", str(items['code']))
    update_subscribe()

    return "OK"


@app.route('/set_subscribe_node', methods=['GET', 'POST'])
def set_subscribe_node():
    items = request.args.to_dict()

    node = int(items['node']) - 1
    change_subscribe_node(node)

#    node = str(items['node'])
#    if node == "1":
#        change_subscribe_node(0)
#    elif node == "2":
#        change_subscribe_node(1)
#    elif node == "3":
#        change_subscribe_node(2)
#    elif node == "4":
#        change_subscribe_node(3)
#    elif node == "5":
#        change_subscribe_node(4)
#    elif node == "6":
#        change_subscribe_node(5)
#    elif node == "7":
#        change_subscribe_node(6)
#    elif node == "8":
#        change_subscribe_node(7)
#    elif node == "9":
#        change_subscribe_node(8)
#    elif node == "10":
#        change_subscribe_node(9)
#    else:
#        change_subscribe_node(0)

    change_panel("config_source", "subscribe.list")
    # gen_server()
    gen_client()
    restart_service()

    return "OK"


@app.route('/set_trans', methods=['GET', 'POST'])
def set_trans():
    items = request.args.to_dict()
    trans = str(items['trans'])
    if trans == "1":
        change_config("trans", "tcp")
        change_config("tls", "off")
    elif trans == "2":
        change_config("trans", "websocket")
        change_config("domain_ip", items['domain'])
        change_config("tls", "on")
    elif trans == "3":
        change_config("trans", "mkcp")
        change_config("tls", "off")
    elif trans == "4":
        change_config("trans", "mkcp-srtp")
        change_config("tls", "off")
    elif trans == "5":
        change_config("trans", "mkcp-utp")
        change_config("tls", "off")
    else:
        change_config("trans", "mkcp-wechat")
        change_config("tls", "off")
    # gen_server()
    gen_client()
    restart_service()

    return "OK"


@app.route('/')
@app.route('/index.html')
def index_page():
    return render_template("index.html")


@app.route('/app.html')
def app_page():
    return render_template("app.html")


@app.route('/log.html')
def log_page():
    return render_template("log.html")


@app.route('/config.html')
def config_page():
    return render_template("config.html")


@app.route('/subscribe.html')
def subscribe_page():
    return render_template("subscribe.html")


@app.route('/get_info')
def get_info():
    with open("panel.config") as panel_config:
        panel = json.load(panel_config)
    with open(panel["config_source"]) as v2ray_config:
        json_content_list = json.load(v2ray_config)
        active = json_content_list["active"]
        json_content = json_content_list["list"][active]

        json_content['status'] = get_status()
        json_dump = json.dumps(json_content_list)

    return json_dump


@app.route('/get_config_info')
def get_config_info():
    with open("config.list") as v2ray_config:
        json_content_list = json.load(v2ray_config)
        active = json_content_list["active"]
        json_content = json_content_list["list"][active]

        json_content['status'] = get_status()
        json_dump = json.dumps(json_content_list)

    return json_dump


@app.route('/get_subscribe_info')
def get_subscribe_info():
    with open("subscribe.list") as v2ray_config:
        json_content_list = json.load(v2ray_config)
        active = json_content_list["active"]
        json_content = json_content_list["list"][active]

        json_content['status'] = get_status()
        json_dump = json.dumps(json_content_list)

    return json_dump


@app.route('/get_panel_info')
def get_panel_info():
    cmd_get_current_ver = """echo `/usr/bin/v2ray/v2ray -version 2>/dev/null` | head -n 1 | cut -d " " -f2"""
    current_ver = 'v' + commands.getoutput(cmd_get_current_ver)
    with open("panel.config") as panel_config:
        json_panel = json.load(panel_config)
        json_panel['v2ray_current_ver'] = str(current_ver)
        change_panel("v2ray_current_ver", str(current_ver))
        json_dump = json.dumps(json_panel)

    return json_dump


@app.route('/get_v2ray_new_ver')
def get_v2ray_new_ver():
    cmd_get_new_ver = """curl -s https://api.github.com/repos/v2ray/v2ray-core/releases/latest --connect-timeout 10| grep 'tag_name' | cut -d '"' -f4"""
    new_ver = commands.getoutput(cmd_get_new_ver)

    with open("panel.config") as panel_config:
        json_panel = json.load(panel_config)
        json_panel['v2ray_new_ver'] = str(new_ver)
        change_panel("v2ray_new_ver", str(new_ver))
        json_dump = json.dumps(json_panel)

    return json_dump


@app.route('/update_v2ray')
def set_update_v2ray():
    update_v2ray()
    with open("panel.config") as panel_config:
        json_panel = json.load(panel_config)
    json_dump = json.dumps(json_panel)
    return json_dump


@app.route('/get_access_log')
def get_access_log():
    with open('/var/log/v2ray/access.log') as f:
        content = f.read().split("\n")
        min_length = min(20, len(content))
        content = content[-min_length:]
        string = ""
        for i in range(min_length):
            string = string + content[i] + "<br>"
    return string


@app.route('/get_error_log')
def get_error_log():
    with open('/var/log/v2ray/error.log') as f:
        content = f.read().split("\n")
        min_length = min(20, len(content))
        content = content[-min_length:]
        string = ""
        for i in range(min_length):
            string = string + content[i] + "<br>"
    return string


app.run(host='0.0.0.0', port=panel_config['port'])

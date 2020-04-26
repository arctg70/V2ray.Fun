#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 生成v2ray的配置，添加socks代理端口
import commands
import json

import requests
from requests.exceptions import ConnectTimeout


def gen_client():
    whitelist_client_raw = """
{
    "log": {
        "access": "/var/log/v2ray/access.log",
        "error": "/var/log/v2ray/error.log",
        "loglevel": "warning"
    },
    "inbounds": [
        {
          "tag": "proxy",
          "port": 10808,
          "listen": "0.0.0.0",
          "protocol": "socks",
          "sniffing": {
            "enabled": true,
            "destOverride": [
              "http",
              "tls"
            ]
          },
          "settings": {
            "auth": "noauth",
            "udp": true,
            "ip": null,
            "address": null,
            "clients": null
          },
          "streamSettings": null
        },
        {
          "port": 12345,
          "protocol": "dokodemo-door",
          "settings": {
               "network": "tcp,udp",
               "followRedirect": true
          }
        },
        {
            "tag": "dns-in",
            "protocol": "dokodemo-door",
            "port": 53,
            "settings": {
                "address": "8.8.8.8",
                "port": 53,
                "network": "udp",
                "followRedirect": false
            }
        }
    ],
	"outbounds": [
		{
			"protocol": "vmess",
			"settings": {
				"vnext": [
					{
						"address": "",
						"port": 39885,
						"users": [
							{
								"id": "475161c6-837c-4318-a6bd-e7d414697de5",
								"alterId": 64,
								"security": "auto"
							}
						]
					}
				]
			},
			"streamSettings": {
				"network": "tcp",
				"security": "none",
				"tlsSettings": null,
				"tcpSettings": null,
				"kcpSettings": null,
				"wsSettings": null,
				"httpSettings": null,
				"quicSettings": null,
				"sockopt": {
					"mark": 255
				}
			},
			"mux": {
				"enabled": false
			}
		},
		{
			"tag": "direct",
			"protocol": "freedom",
			"settings": {},
			"streamSettings": {
				"sockopt": {
					"mark": 255
				}
			}
		},
		{
			"protocol": "dns",
			"tag": "dns-out"
		}
	],
	"dns": {
		"servers": [
			"8.8.8.8",
			"8.8.4.4",
			{
				"address": "114.114.114.114",
				"port": 53,
				"domains": [
					"geosite:cn",
					"geosite:speedtest"
				]
			}
		]
	},
	"routing": {
		"domainStrategy": "IPIfNonMatch",
		"rules": [
			{
				"type": "field",
				"inboundTag": [
					"dns-in"
				],
				"outboundTag": "dns-out"
			},
			{
				"type": "field",
				"outboundTag": "direct",
				"ip": [
					"geoip:private"
				]
			},
			{
				"type": "field",
				"outboundTag": "direct",
				"ip": [
					"geoip:cn"
				]
			},
			{
				"type": "field",
				"outboundTag": "direct",
				"domain": [
					"geosite:cn",
					"geosite:speedtest"
				]
			}
		]
	}
}
    """

    global_client_raw = """
{
    "log": {
        "access": "/var/log/v2ray/access.log",
        "error": "/var/log/v2ray/error.log",
        "loglevel": "warning"
    },
	"inbounds": [
      {
      "tag": "proxy",
      "port": 10808,
      "listen": "0.0.0.0",
      "protocol": "socks",
      "sniffing": {
        "enabled": true,
        "destOverride": [
          "http",
          "tls"
        ]
      },
      "settings": {
        "auth": "noauth",
        "udp": true,
        "ip": null,
        "address": null,
        "clients": null
      },
      "streamSettings": null
    },
		{
			"port": 12345,
			"protocol": "dokodemo-door",
			"settings": {
				"network": "tcp,udp",
				"followRedirect": true
			}
		},
		{
			"protocol": "dokodemo-door",
			"port": 53,
			"settings": {
				"address": "8.8.8.8",
				"port": 53,
				"network": "udp",
				"followRedirect": false
			}
		}
	],
	"outbounds": [
		{
			"protocol": "vmess",
			"settings": {
				"vnext": [
					{
						"address": "",
						"port": 39885,
						"users": [
							{
								"id": "475161c6-837c-4318-a6bd-e7d414697de5",
								"alterId": 64,
								"security": "auto"
							}
						]
					}
				]
			},
			"streamSettings": {
				"network": "tcp",
				"security": "none",
				"tlsSettings": null,
				"tcpSettings": null,
				"kcpSettings": null,
				"wsSettings": null,
				"httpSettings": null,
				"quicSettings": null,
				"sockopt": {
					"mark": 255
				}
			},
			"mux": {
				"enabled": false
			}
		}
	]
}
    """

    direct_client_raw = """
{
    "log": {
        "access": "/var/log/v2ray/access.log",
        "error": "/var/log/v2ray/error.log",
        "loglevel": "warning"
    },
	"inbounds": [
      {
      "tag": "proxy",
      "port": 10808,
      "listen": "0.0.0.0",
      "protocol": "socks",
      "sniffing": {
        "enabled": true,
        "destOverride": [
          "http",
          "tls"
        ]
      },
      "settings": {
        "auth": "noauth",
        "udp": true,
        "ip": null,
        "address": null,
        "clients": null
      },
      "streamSettings": null
    },
		{
			"port": 12345,
			"protocol": "dokodemo-door",
			"settings": {
				"network": "tcp,udp",
				"followRedirect": true
			}
		},
		{
			"protocol": "dokodemo-door",
			"port": 53,
			"settings": {
				"address": "114.114.114.114",
				"port": 53,
				"network": "udp",
				"followRedirect": false
			}
		}
	],
	"outbounds": [
		{
			"protocol": "freedom",
			"settings": {},
			"streamSettings": {
				"sockopt": {
					"mark": 255
				}
			}
		}
	]
}
    """

    cLient_mkcp = json.loads("""
    {
                "mtu": 1350,
                "tti": 50,
                "uplinkCapacity": 20,
                "downlinkCapacity": 100,
                "congestion": true,
                "readBufferSize": 2,
                "writeBufferSize": 2,
                "header": {
                    "type": "none"
                }
    }
    """)

    cLient_ws = json.loads("""
    {
					"connectionReuse": true,
					"path": null,
					"headers": null
	}
    """)

    mux_enable = json.loads("""
    {
            "enabled": true
    }
    """)

    mux_disable = json.loads("""
    {
            "enabled": false
    }
    """)
    with open("panel.config") as panel:
        panel_config = json.load(panel)
        config_source = panel_config['config_source']
    if panel_config['routing'] == "direct":
        client = json.loads(direct_client_raw)
        with open("/etc/v2ray/config.json", "w") as f:
            f.write(json.dumps(client, indent=2))
        return
    elif panel_config['routing'] == "whitelist":
        client = json.loads(whitelist_client_raw)
    elif panel_config['routing'] == "global":
        client = json.loads(global_client_raw)

    with open(config_source) as f:
        data_list = json.load(f)
        active = data_list['active']
        data = data_list['list'][active]

    if data['mux'] == "on":
        client['outbounds'][0]['mux']['enabled'] = True
    elif data['mux'] == "off":
        client['outbounds'][0]['mux']['enabled'] = False

    client['outbounds'][0]['settings']['vnext'][0]['address'] = data['domain_ip']
    client['outbounds'][0]['settings']['vnext'][0]['port'] = int(data['port'])
    client['outbounds'][0]['settings']['vnext'][0]['users'][0]['id'] = data['uuid']
    client['outbounds'][0]['settings']['vnext'][0]['users'][0]['security'] = data['encrypt']

    if data['trans'] == "websocket":
        client['outbounds'][0]['streamSettings']['network'] = "ws"
        cLient_ws['path'] = data['wspath']
        client['outbounds'][0]['streamSettings']['wsSettings'] = cLient_ws

    elif data['trans'].startswith("mkcp"):
        if data['trans'] == "mkcp-srtp":
            cLient_mkcp['header']['type'] = "srtp"
        elif data['trans'] == "mkcp-utp":
            cLient_mkcp['header']['type'] = "utp"
        elif data['trans'] == "mkcp-wechat":
            cLient_mkcp['header']['type'] = "wechat-video"

        client['outbounds'][0]['streamSettings']['network'] = "kcp"
        client['outbounds'][0]['streamSettings']['kcpSettings'] = cLient_mkcp

    elif data['trans'] == "tcp":
        client['outbounds'][0]['streamSettings']['network'] = "tcp"

    if data['tls'] == "on":
        client['outbounds'][0]['streamSettings']['security'] = "tls"

    with open("/etc/v2ray/config.json", "w") as f:
        f.write(json.dumps(client, indent=2))
    # with open("/root/config.json", "w") as f:
    #    f.write(json.dumps(client, indent=2))

    # with open("/usr/local/V2ray.Fun/static/config.json", "w") as f:
    #    f.write(json.dumps(client, indent=2))

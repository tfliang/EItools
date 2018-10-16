import json
import re
import time
from urllib import request

import cchardet
import requests


class Proxy:

    def __init__(self, conf):
        self.server = conf['server']
        if 'interval' in conf:
            self.interval = conf['interval']
        else:
            self.interval = 300
        self.last_time = time.time()

    def is_available(self):
        return time.time() - self.last_time > self.interval


class ProxySwitcher:

    def __init__(self):
        self.proxies = []
        self.current_proxy_index = -1
        self.get_proxy_list()

    def add_proxy(self, proxy):
        if type(proxy) is Proxy:
            self.proxies.append(proxy)
        if type(proxy) is str:
            self.add_proxy_by_server(proxy)
        if type(proxy) is dict:
            self.add_proxy_by_server(proxy)
            #self.add_proxy_by_conf(proxy)
        if type(proxy) is list:
            for p in proxy:
                self.add_proxy(p)

    def add_proxy_by_conf(self, conf):
        proxy = Proxy(conf)
        self.add_proxy(proxy)

    def add_proxy_by_server(self, server):
        conf = {'server': server}
        proxy = Proxy(conf)
        self.add_proxy(proxy)

    def get_proxy(self):
        def return_proxy(index):
            self.current_proxy_index = index
            self.proxies[index].last_time = time.time()
            return True, self.proxies[index].server
        if len(self.proxies) > 0:
            if self.current_proxy_index < 0:
                return return_proxy(0)
            if time.time()-self.proxies[self.current_proxy_index].last_time<self.proxies[self.current_proxy_index].interval:
                return return_proxy(self.current_proxy_index)
            index = self.current_proxy_index + 1
            for i in range(index, len(self.proxies)):
                if self.proxies[i].is_available():
                    return return_proxy(i)
            for i in range(0, index):
                if self.proxies[i].is_available():
                    return return_proxy(i)

        return False, ''

    def get_proxy_by_url(self):
        #if need==False:
            #proxy_id = "50246453887904920091"
            #content = request.urlopen(
             #   "http://api.baibianip.com/api/changeip?apikey=8035c3345550bb41834c60a298c9df02&format=json&proxy_id={}".format(
                    #proxy_id))
        #proxy_id_content = request.urlopen(
            #"http://api.baibianip.com/api/getproxy?gettype=exclusive&apikey=8035c3345550bb41834c60a298c9df02&format=json").read()
        #proxy_id_data = json.loads(proxy_id_content)
        #if proxy_id_data['errmsg']=="SUCCESS":
            #return True,"{}:{}".format(proxy_id_data['proxy_list'][0]['proxy_ip'],proxy_id_data['proxy_list'][0]['proxy_port'])
        #return False,""
        r=requests.get("http://localhost:8899/api/v1/proxies")

        content = r.content
        charset = cchardet.detect(content)
        text = content.decode(charset['encoding'])
        proxy_ids = json.loads(str(text))
        return "{}:{}".format(proxy_ids['proxies'][0]['ip'],proxy_ids['proxies'][0]['port'])

    def get_proxy_list(self):
        r=requests.get("https://luminati-china.io/api/get_route_ips",headers={"X-Hola-Auth": "lum-customer-hl_0079c473-zone-static-key-guuvbtwyulfj-country-us"})
        content = r.content
        charset = cchardet.detect(content)
        text = content.decode(charset['encoding'])
        ip_list=re.split(r'[\n\r]',text)
        for ip in ip_list:
            proxy_ip={'http':'https://{}'.format(ip)}
            self.add_proxy(proxy_ip)


    def get_proxy_list2(self):
        PROXIES = [{  # Linux or Mac: Polipo (http->socks5) + ss (socks5->google)
            'http': 'http://127.0.0.1:1087',
            'https': 'http://127.0.0.1:1087'
        }]
        self.add_proxy(PROXIES)
        return PROXIES

proxy_switch=ProxySwitcher()




# url=ProxySwitcher().get_proxy_by_url()
# print("https://"+url)
# print(requests.get("http://www.google.com",proxies={'https':"https://212.93.119.116:8080"}))






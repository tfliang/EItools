import time


class Proxy:

    def __init__(self, conf):
        self.server = conf['server']
        if 'interval' in conf:
            self.interval = conf['interval']
        else:
            self.interval = 0
        self.last_time = time.time()

    def is_available(self):
        return time.time() - self.last_time > self.interval


class ProxySwitcher:

    def __init__(self):
        self.proxies = []
        self.current_proxy_index = -1

    def add_proxy(self, proxy):
        if type(proxy) is Proxy:
            self.proxies.append(proxy)
        if type(proxy) is str:
            self.add_proxy_by_server(proxy)
        if type(proxy) is dict:
            self.add_proxy_by_conf(proxy)
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
            if index != self.current_proxy_index:
                self.current_proxy_index = index
                self.proxies[index].last_time = time.time()
                return True, self.proxies[index].server
            else:
                return False, ''
        if len(self.proxies) > 0:
            if self.current_proxy_index < 0:
                return return_proxy(0)
            index = self.current_proxy_index + 1
            for i in range(index, len(self.proxies) - 1):
                if self.proxies[i].is_available():
                    return return_proxy(i)
            for i in range(0, index):
                if self.proxies[i].is_available():
                    return return_proxy(i)

        return False, ''

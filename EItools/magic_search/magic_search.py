import os
import random
import sys
import time

import cchardet
import requests
from bs4 import BeautifulSoup

from pyquery import PyQuery as pq
from MagicGoogle.config import USER_AGENT, DOMAIN, BLACK_DOMAIN, URL_SEARCH, URL_NEXT, URL_NUM

from EItools.log.log import logger

from urllib.parse import quote_plus, urlparse, parse_qs
from EItools.chrome.proxy import proxy_switch


class MagicSearch():
    """
    Magic google search.
    """

    def __init__(self, proxies=None):
        result,proxies = proxy_switch.get_proxy()
        self.proxies={'http':"http://"+proxies}

    def search(self, query, language=None, num=None, start=0, pause=2):
        """
        Get the results you want,such as title,description,url
        :param query:
        :param language:
        :param num:
        :param start:
        :return: Generator
        """
        content = self.search_page(query, language, num, start, pause)
        pq_content = self.pq_html(content)
        for item in pq_content('div.g').items():
            result = {}
            result['title'] = item('h3.r>a').eq(0).text()
            href = item('h3.r>a').eq(0).attr('href')
            if href:
                url = self.filter_link(href)
                result['url'] = url
            text = item('span.st').text()
            result['text'] = text
            yield result

    def search_page(self, query, language=None, num=None, start=0, pause=2):
        """
        Google search
        :param query: Keyword
        :param language: Language
        :return: result
        """
        time.sleep(pause)
        domain = self.get_random_domain()
        if start > 0:
            url = URL_NEXT
            url = url.format(
                domain=domain, language=language, query=quote_plus(query), num=num, start=start)
        else:
            if num is None:
                url = URL_SEARCH
                url = url.format(
                    domain=domain, language=language, query=quote_plus(query))
            else:
                url = URL_NUM
                url = url.format(
                    domain=domain, language=language, query=quote_plus(query), num=num)
        if language is None:
            url = url.replace('hl=None&', '')
        # Add headers
        headers = {'user-agent': self.get_random_user_agent()}
        try:
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
            result,proxies = proxy_switch.get_proxy()
            self.proxies = {'http': "http://" + proxies}
            print(self.proxies)
            r = requests.get(url=url,
                             proxies=self.proxies,
                             headers=headers,
                             allow_redirects=False,
                             verify=False,
                             timeout=30)
            logger.info(url)
            content = r.content
            charset = cchardet.detect(content)
            text = content.decode(charset['encoding'])
            return text
        except Exception as e:
            logger.exception(e)
            return None

    def search_baidu(self, query, start=0, pause=2):
        """
        Get the results you want,such as title,description,url
        :param query:
        :param start:
        :return: Generator
        """
        start = start // 10 * 10
        content = self.search_page(query, start, pause)
        soup = BeautifulSoup(content, "html.parser")
        now = start + 1
        for item in soup.find_all(attrs={'class': 'c-container'}):
            result = {}
            result['title'] = item.h3.get_text()
            result['url'] = item.h3.a['href']
            ss = ''
            for div in item.find_all('div'):
                if div.has_attr('class') and (div['class'][0].find('abstract') != -1 or div['class'][0] == 'c-row'):
                    ss += div.get_text()
                domain = div.find(attrs={'class': 'c-showurl'})
                if domain is not None:
                    result['domain'] = domain.get_text()
            result['text'] = ss
            yield result

    def search_page_baidu(self, query, start=0, pause=2):
        """
        Baidu search
        :param query: Keyword
        :param language: Language
        :return: result
        """
        start = start // 10 * 10
        time.sleep(pause)
        param = {'wd': query, 'pn': str(start)}
        url = 'https://www.baidu.com/s'
        # Add headers
        headers = {'user-agent': self.get_random_user_agent(),
                   'host': 'www.baidu.com',
                   'referer': 'https://www.baidu.com/s',
                   'is_referer': 'https://www.baidu.com/s'
                   }
        try:
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(url=url,
                             params=param,
                             headers=headers,
                             allow_redirects=False,
                             verify=False,
                             timeout=10)
            content = r.content
            charset = cchardet.detect(content)
            text = content.decode(charset['encoding'])
            return text
        except:
            return None

    def search_url(self, query, language=None, num=None, start=0, pause=2):
        """
        :param query:
        :param language:
        :param num:
        :param start:
        :return: Generator
        """
        content = self.search_page(query, language, num, start, pause)
        pq_content = self.pq_html(content)
        for item in pq_content('h3.r').items():
            href = item('a').attr('href')
            if href:
                url = self.filter_link(href)
                if url:
                    yield url

    def filter_link(self, link):
        """
        Returns None if the link doesn't yield a valid result.
        Token from https://github.com/MarioVilas/google
        :return: a valid result
        """
        try:
            # Valid results are absolute URLs not pointing to a Google domain
            # like images.google.com or googleusercontent.com
            o = urlparse(link, 'http')
            if o.netloc:
                return link
            # Decode hidden URLs.
            if link.startswith('/url?'):
                link = parse_qs(o.query)['q'][0]
                # Valid results are absolute URLs not pointing to a Google domain
                # like images.google.com or googleusercontent.com
                o = urlparse(link, 'http')
                if o.netloc:
                    return link
        # Otherwise, or on error, return None.
        except Exception as e:
            logger.exception(e)
            return None

    def pq_html(self, content):
        """
        Parsing HTML by pyquery
        :param content: HTML content
        :return:
        """
        return pq(content)

    def get_random_user_agent(self):
        """
        Get a random user agent string.
        :return: Random user agent string.
        """
        return random.choice(self.get_data('user_agents.txt', USER_AGENT))

    def get_random_domain(self):
        """
        Get a random domain.
        :return: Random user agent string.
        """
        domain = random.choice(self.get_data('all_domain.txt', DOMAIN))
        if domain in BLACK_DOMAIN:
            self.get_random_domain()
        else:
            return domain

    def get_data(self, filename, default=''):
        """
        Get data from a file
        :param filename: filename
        :param default: default value
        :return: data
        """
        root_folder = os.path.dirname(__file__)
        user_agents_file = os.path.join(
            os.path.join(root_folder, 'data'), filename)
        try:
            with open(user_agents_file) as fp:
                data = [_.strip() for _ in fp.readlines()]
        except:
            data = [default]
        return data

    def get_webpage_content(self,url):
        headers = {'user-agent': self.get_random_user_agent()}
        result, proxies = proxy_switch.get_proxy()
        self.proxies = {'http': "http://" + proxies}
        res = requests.get(url, headers=headers,proxies=self.proxies)
        # res.encoding='utf-8'
        content = res.content
        return content

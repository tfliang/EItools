import json
import time

import bs4
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import sys
from EItools.log.log import logger

from selenium.webdriver.common.keys import Keys

from EItools.chrome import proxy


class ChromeCrawler:
    def __init__(self,dict_options):
        self.killed=False
        chrome_options=Options()
        chrome_options.add_argument('--disable-extensions')
        if 'debug' not in str(sys.argv):
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        self.options=chrome_options
        self.proxy_switcher = proxy.ProxySwitcher()
        if "proxy" in dict_options:
            self.proxy_switcher.add_proxy(dict_options["proxy"])
        self.switch_proxy(need=False)
        self.parse_info=dict_options["parse_info"]
        self.homepage=dict_options["homepage"]
        self.name=dict_options["name"]
        self.start()

    def start(self):
        logger.info("chrome [%s] starting,home is [%s]",self.name,self.homepage)
        self.driver=webdriver.Chrome(chrome_options=self.options)
        self.driver.get(self.homepage)
        time.sleep(3)
        logger.info("chrome [%s] started home is [%s]",self.name,self.homepage)

    def shutdown(self):
        logger.info("chrome [%s] closing,home is [%s]",self.name,self.homepage)
        try:
            self.driver.close()
        except Exception as e:
            logger.error("%s, %s",self.name,e)
        self.driver.quit()
        logger.info("chrome [%s] closed,home is [%s]",self.name,self.homepage)


    def switch_proxy(self,need=True):
        #is_switch, proxy = self.proxy_switcher.get_proxy()
        is_switch,proxy=self.proxy_switcher.get_proxy_by_url(need)
        if is_switch:
            arg_proxy = '--proxy-server='
            for arg in self.options.arguments:
                if arg.startswith(arg_proxy):
                    self.options.arguments.remove(arg)
                    break
            self.options.add_argument(arg_proxy + proxy)
        return is_switch

    def download_parse(self,keyword):
        logger.info(keyword)
        page=self.download_page(keyword)
        return self.parse_page(page)

    def download_page(self,keyword,retries=0):
        def retry(count):
            try:
                if count>3:
                    return None
                time.sleep(30)
                self.shutdown()
                self.start()
                return self.download_page(keyword,count)
            except Exception as e:
                logger.error("retry error:%s,%s,have retried %d times",self.name,e,count)
                return retry(count+1)
        source_code='blank'
        try:
            if self.killed:
                self.shutdown()
                return None
            element = self.driver.find_element_by_tag_name("body")
            source_code = element.get_attribute("outerHTML")
            print(source_code)
            search_box=self.driver.find_element_by_name(self.parse_info['search_box_name'])
            search_box.clear()
            search_box.send_keys(keyword)
            time.sleep(1)
            search_box.send_keys(Keys.RETURN)
            elem=self.driver.find_element_by_xpath("//*")
            source_code=elem.get_attribute("outerHTML")
            if 'www.google.com/recaptcha' in source_code:
                source_code="recaptcha"
                logger.info("enter recaptcha")
                self.driver.switch_to.frame(self.driver.find_element_by_tag_name("iframe"))
                for clickCount in range(1,6):
                    element=self.driver.find_element_by_id("recaptcha-anchor")
                    logger.info("find recaptcha checked: %s",element.get_attribute("aria-checked"))
                    self.driver.execute_script("arguments[0].click();",element)
                    logger.info("click recaptcha %s times",clickCount)
                    time.sleep(5)
                    element=self.driver.find_element_by_id("recaptcha-anchor")
                    result=element.get_attribute("aria-checked")
                    logger.info("click result:%s",result)
                    if "true" in str(result):
                        self.driver.switch_to.default_content()
                        btn=self.driver.find_element_by_name("submit")
                        btn.submit()
                        time.sleep(5)
                        elem=self.driver.find_element_by_xpath("//*")
                        source_code=elem.get_attribute("outerHTML")
                        break
                    else:
                        if clickCount==5:
                            logger.info("recaptcha fail.sleep 1 hour")
                            for i in range(1,360):
                                if self.killed:
                                    self.shutdown()
                                    return None
                                if i%30==0:
                                    print("have sleep 5 minute")
                                source_code = elem.get_attribute("outerHTML")
                                if self.switch_proxy():
                                    return retry(retries)
                                time.sleep(10)
            self.driver.find_element_by_name(self.parse_info['search_box_name'])
            return source_code
        except Exception as e:
            if type(e) is not NoSuchElementException:
                logger.info("download page %s"%(e))
                source_code="other error"
            logger.error("%s,%s, \n%s, have retried %d times",self.name,e,source_code,retries)
            retries+=1
            return retry(retries)

    def parse_page(self,gpage):
        def parse_snippet(snippet):
            try:
                title=' '.join(snippet.find(
                    self.parse_info['title_tag']).a.strings)
                title_src=''.join(snippet.find(self.parse_info['title_tag']).a['href'])
                if 'content_tag' in self.parse_info:
                    if 'content_cls' in self.parse_info:
                        content=''.join(snippet.find(
                            self.parse_info['content_tag'],class_=self.parse_info['content_cls']).strings).replace('\n','')
                    else:
                        content=''.join(snippet.find(
                            self.parse_info['content_tag']).strings).replace('\n','')
                else:
                    content=""
                h_keywords=[]
                if 'h_tag' in self.parse_info:
                    for t in snippet.find_all(self.parse_info['h_tag']):
                        h_keywords.append(t.string)
                return {
                    'title':title,
                    'content':content,
                    'page_src':title_src,
                    'h_keywords':h_keywords
                }
            except Exception as e:
                #logger.info(e)
                return None

        if not gpage:
            return []

        soup=bs4.BeautifulSoup(gpage,'html.parser')
        if 'snippet_cls' in self.parse_info:
            snippets=soup.find_all(
                self.parse_info['snippet_tag'],class_=self.parse_info['snippet_cls'])
        else:
            snippets=soup.find_all(self.parse_info['snippet_tag'])

        if not snippets and "did not match any documents" not in gpage:
            logger.error("%s parse error for page %s",self.name,"snipptes none")
            time.sleep(20)

        snippets=[parse_snippet(s) for s in snippets]
        snippets=[s for s in snippets if s]
        nsnippets=len(snippets)
        for i in range(nsnippets):
            snippets[i]['pos']=i+1
            snippets[i]['src']=self.name

        return snippets

    def get_main_page(self,url,person):
        try:
            self.driver.get(url)
            element=self.driver.find_element_by_class_name("main-content")
            source_code = element.get_attribute("outerHTML")
            soup = bs4.BeautifulSoup(source_code, 'html.parser')
            text=soup.get_text(separator="")
            lines = (line.strip() for line in text.splitlines())
            text = '\n\r'.join(chunk for chunk in lines if chunk)
        except Exception as e:
            if type(e) is NoSuchElementException:
                try:
                    element=self.driver.find_element_by_tag_name("body")
                    soup=bs4.BeautifulSoup(element.get_attribute("outerHTML"),'html.parser')
                    scripts=soup.find_all(name='div',attrs={"class":re.compile(r'.*(foot|nav|Nav|footer|bottom|pageR_t clearfix|menu|header|left).*$')})
                    scriptsId=soup.find_all(name='div',attrs={"id":re.compile(r'.*(foot|nav|Nav|footer|bottom|pageR_t clearfix|header|guest|head|left).*$')})
                    for script in scripts+scriptsId:
                        script.extract()
                    for script in soup(["script", "style"]):
                        script.extract()
                    text = soup.find('body').get_text(separator="")
                    #lines = (line.strip() for line in text.splitlines())
                    #text = '\n\r'.join(chunk for chunk in lines if chunk)
                    lines = (line.strip() for line in text.split())
                    if person['ini'].find("公司") != -1:
                        text = '\n\r'.join(chunk for chunk in lines if chunk.find(person['name'])!=-1)
                    else:
                        text = '\n\r'.join(chunk for chunk in lines if chunk)
                except Exception as e:
                    logger.info(e)
                    text=""
            else:
                logger.info(e)
                text=""
        # try:
        #     self.driver.get(self.homepage)
        # except Exception as e:
        #     time.sleep(3)
        #     logger.info(e)
        #     self.shutdown()
        #     self.start()
        return text

    def get_scholar_citation(self,url):
        try:
            self.driver.get(url)
            element=self.driver.find_element_by_id("gsc_rsb_st")
            source_code = element.get_attribute("outerHTML")
            soup = bs4.BeautifulSoup(source_code, 'html.parser')
            content=soup.get_text(separator="<k>")
        except Exception as e:
            logger.info(e)
            content=""
        try:
            self.driver.get(self.homepage)
        except Exception as e:
            time.sleep(3)
            logger.info(e)
            self.shutdown()
            self.start()
        return content



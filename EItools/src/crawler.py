#coding:utf-8
import json
import string
import sys
import re

import bs4
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from EItools.log.log import logger
from EItools.src import globalvar
from EItools.src.chrome import ChromeCrawler
from EItools.utils import chinese_helper


class PhoneCrawler:
    crawlers = []
    def load_crawlers(self):
        with open(globalvar.FILE_CONFIG) as f:
            config_crawlers=json.load(f)
        for crawler_config in config_crawlers:
                crawler=ChromeCrawler(crawler_config)
                self.crawlers.append(crawler)
    def shutdown_crawlers(self):
        for c in self.crawlers:
            c.shutdown()
    def kill_crawlers(self):
        for c in self.crawlers:
            c.killed=True

    def get_phones(self,person):
        eps=[]
        for crawler in self.crawlers:
            #classfier=Classifier()
            content,url=self.get_information(crawler,person,aff=True)
            return content,url
            #eps=classfier.get_eps(snippets,person)
            #if 'simple' in person and len(person['simple'].split(' '))>11 and len(eps)>0 and eps[0][1]<0.9:
                #snippets=get_snippets(crawler,person,aff=False)
                #eps=classfier.get_eps(snippets,person)
            #if eps and eps[0][1]>=0.9:
                #return eps

    def get_info(self, person):
        eps = []
        for crawler in self.crawlers:
            # classfier=Classifier()
            content, url = self.get_information(crawler, person, aff=True)
            return content, url
            # eps=classfier.get_eps(snippets,person)
            # if 'simple' in person and len(person['simple'].split(' '))>11 and len(eps)>0 and eps[0][1]<0.9:
            # snippets=get_snippets(crawler,person,aff=False)
            # eps=classfier.get_eps(snippets,person)
            # if eps and eps[0][1]>=0.9:
            # return eps

    def get_snippets(self,crawler,person,aff=True):
        template='phone'
        if aff:
            template='{} '.format(person['simple_affiliation'])+template
        snippets=crawler.download_parse('{} '.format(person['name'])+template)
        logger.info(snippets)
        if 'name_zh' in person and len(person['name_zh']):
            snippets2=crawler.download_parse(
                '{} '.format(person['name_zh'])+template)
            snippets+=snippets2

        #get the possible main page
        page_snippets=self.filt_page(snippets,person)

        # go to main page
        content = ""
        for snippet in page_snippets:
            content=crawler.get_main_page(snippet["page_src"])
        return content

    def get_information(self,crawler,person,aff=True):
        if aff:
            template = '{} '.format(person['simple_affiliation'])
        else:
            template=""
        snippets = crawler.download_parse('{} '.format(person['name']) + template)
        if 'name_zh' in person and len(person['name_zh']):
            snippets2 = crawler.download_parse(
                '{} '.format(person['name_zh']) + template)
            snippets += snippets2
        # go to main page
        content= ""
        url=""
        page_snippets = self.filt_page(snippets,person)
        for snippet in page_snippets:
            logger.info("page_src  "+snippet["page_src"])
            content = crawler.get_main_page(snippet["page_src"])
            url=snippet["page_src"]
            if content!="":
                break
        logger.info("page_src " + url)
        return content,url


    def match_phone(self,content):
        phones=[]
        tel_pattern=re.compile(r'(0[0-9]{2,3}/-)?([2-9][0-9]{6,7})+(/-[0-9]{1,4})?')
        tel_match=tel_pattern.findall(content)
        mobile_pattern =re.compile("((/(/d{3}/))|(/d{3}/-))?13[456789]/d{8}|15[89]/d{8}")
        mobile_match=mobile_pattern.findall(content)

        print(len(mobile_match))
        print(len(tel_match))
        if len(tel_match)>0:
            phones.append(tel_match)
        if len(mobile_match)>0:
            phones.append(mobile_match)
        return phones

    def filt_phone(self,snippets):
        def pfilter(snippet):
            snippet['phones']=self.match_phone(snippet["content"])
            return snippet
        snippets=[pfilter(s) for s in snippets]
        snippets=[s for s in snippets if s['phones']]
        return snippets

    #with open('../dict.json') as f:
        #data=json.loads(f.read())

    def cal_sparse_tf_idf(corpus,test_corpus):
        vectorizer=CountVectorizer()
        transformer=TfidfTransformer()
        tfidf=transformer.fit_transform(corpus)
        test_tf=vectorizer.transform(test_corpus)
        test_tf_idf=transformer.transform(test_tf)
    # def contain_orgName(url,orgName):
    #     tf=0
    #     if contain_zh(orgName):
    #         orgName=translate(orgName)
    #     for word in orgName.split():
    #         if word in url:
    #             tf+=1
    #             if word in data:
    #                 idf=data[word]
    #     tf=2
    #     idf=3
    #     return tf*idf
    # def match_page(self,snippet,person,pos):
    #     print(snippet['page_src'])
    #     keywords_names=chinese_helper.recognize_keywords(snippet['content'])+chinese_helper.recognize_keywords(snippet['title'])
    #     sim_arr_name=[0]
    #     for k_n in set(keywords_names):
    #         sim_arr_name.append(chinese_helper.simila_name(k_n,person['name_zh'] if 'name_zh' in person else person['name']))
    #     sim_nam=max(sim_arr_name)
    #     if sim_nam==0 and person['name'] in snippet['content'] or person[''] in snippet['title']:
    #         sim_nam=1
    #     keywords_orgs=chinese_helper.recognize_keywords(snippet['content'],'nt')+chinese_helper.recognize_keywords(snippet['title'],'nt')
    #     sim_arr_org = [0]
    #     for k_n in set(keywords_orgs):
    #         for org in person['simple_affiliation']:
    #             sim_arr_org.append(chinese_helper.simila_name(k_n,org))
    #     sim_org= max(sim_arr_org)
    #     if sim_org==0 and sim_org in snippet['content'] or sim_org in snippet['title']:
    #         sim_org=1
    #     if sim_nam>0.3 and sim_org>0.3:
    #         if snippet['page_src'].find('baike.baidu.com')!=-1 or snippet['page_src'].find('edu.cn')!=-1:
    #             snippet['importance']=0.5*sim_nam+0.5*sim_org+0.2+1/(pos+2)
    #         else:
    #             snippet['importance']=0.5*sim_nam+0.5*sim_org+1/(pos+2)
    #         return snippet
    def match_page(self, snippet, person, pos):
        keywords_names=snippet['h_keywords'].split(" ")
        keywords_orgs=snippet['h_keywords'].split(" ")
        sim_arr_name=[0]
        for k_n in set(keywords_names):
            sim_arr_name.append(chinese_helper.simila_name(k_n,person['name_zh'] if 'name_zh' in person else person['name']))
        sim_nam=max(sim_arr_name)
        sim_arr_org = [0]
        for k_n in set(keywords_orgs):
            for org in person['simple_affiliation']:
                sim_arr_org.append(chinese_helper.simila_name(k_n,org))
        sim_org= max(sim_arr_org)
        if sim_nam>0.3 and sim_org>0:
            if snippet['page_src'].find('baike.baidu.com')!=-1 or snippet['page_src'].find('edu.cn')!=-1:
                if snippet['title'].find("主页")!=-1:
                    if snippet['title'].find(person['name'])!=-1:
                        snippet['importance']=0.5*sim_nam+0.5*sim_org+0.2+1/(pos+2)+0.2+0.2
                    else:
                        snippet['importance'] = 0.5 * sim_nam + 0.5 * sim_org + 0.2 + 1 / (pos + 2) + 0.2
                else:
                    snippet['importance'] = 0.5 * sim_nam + 0.5 * sim_org + 0.2 + 1 / (pos + 2)
            else:
                snippet['importance']=0.5*sim_nam+0.5*sim_org+1/(pos+2)
            return snippet

    def filt_page(self,snippets,person):
        def filter(snippet,pos):
            return self.match_page(snippet,person,pos)
        snippets=[filter(s,pos) for pos,s in enumerate(snippets)]
        snippets=[s for s in snippets[:3] if s is not None and 'importance' in s]
        return sorted(snippets,key=lambda s:s['importance'],reverse=True)



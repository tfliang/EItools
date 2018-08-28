#coding:utf-8
import json
import re

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from EItools.chrome.chrome import ChromeCrawler
from EItools.chrome.classifier import Classifier
from EItools.config import globalvar
from EItools.log.log import logger
from EItools.utils import chinese_helper


#from EItools.plug.MagicGoogle.magic_google import MagicGoogle

class InfoCrawler:
    crawlers = dict()
    def load_crawlers(self):
        with open(globalvar.FILE_CONFIG) as f:
            config_crawlers=json.load(f)
        for key,crawler_config in config_crawlers.items():
                crawler=ChromeCrawler(crawler_config)
                self.crawlers[key]=crawler
    def shutdown_crawlers(self):
        for _,c in self.crawlers.items():
            c.shutdown()
    def kill_crawlers(self):
        for _,c in self.crawlers:
            c.killed=True

    def get_info(self, person,crawler_key="google"):
        eps = []
        crawler=self.crawlers[crawler_key]
        content, url = self.get_information(crawler, person, aff=True)
        return content, url

    def get_emails(self,person,crawler_key="google"):
        eps = []
        crawler=self.crawlers[crawler_key]
        classifier = Classifier()
        snippets = self.get_snippets(crawler, person, aff=True)
        eps = classifier.get_eps(snippets, person)

        if len(eps) > 0 and eps[0][1] < 0.9:
            snippets = self.get_snippets(crawler, person, aff=False)
            eps = classifier.get_eps(snippets, person)

        if eps and eps[0][1] >= 0.9:
            return eps

        return eps

    def get_scholar_info(self,person,aff=True,crawler_key="google-scholar"):
        if aff:
            template = '{} {}'.format(chinese_helper.translate(person['name'], fromLang="zh", toLang="en")
                                      ,chinese_helper.translate(' '.join(person['simple_affiliation']),fromLang="zh",toLang="en"))
        else:
            template=chinese_helper.translate(person['name'],fromLang="zh",toLang="en")
        crawler=self.crawlers[crawler_key]
        snippets=crawler.download_parse(template)
        citation,h_index, citation_in_recent_five_year=0,0,0
        if len(snippets)>0:
            content=crawler.get_scholar_citation("https://scholar.google.com/"+snippets[0]['page_src'])
            lines=re.split("<k>",content)
            citation=lines[3]
            h_index=lines[6]
            citation_in_recent_five_year=lines[7]
        return citation,h_index,citation_in_recent_five_year

    def get_snippets(self,crawler,person,aff=True):
        template='email'
        if aff:
            template='{} '.format(person['simple_affiliation'])+template
        snippets=crawler.download_parse('{} '.format(person['name'])+template)
        if 'name_zh' in person and len(person['name_zh']):
            snippets2=crawler.download_parse(
                '{} '.format(person['name_zh'])+template)
            snippets+=snippets2
        return self.filt_email(snippets)

    def get_information(self,crawler,person,aff=True):
        if aff:
            template = '{} '.format(person['simple_affiliation'])
        else:
            template=""
        snippets = crawler.download_parse('{} '.format(person['name']) + template)
        if 'name_zh' in person and len(person['name_zh']):
            snippets_of_name_zh = crawler.download_parse(
                '{} '.format(person['name_zh']) + template)
            snippets += snippets_of_name_zh
        # go to main page
        content= ""
        url=""
        page_snippets = self.filt_page(snippets,person)
        for snippet in page_snippets:
            logger.info("page_src  "+snippet["page_src"])
            content = crawler.get_main_page(snippet["page_src"],person)
            url=snippet["page_src"]
            if content!="":
                break
        logger.info("final page_src " + url)
        return content,url

    def match_emails(self,content):
        emails = []
        rough_pattern = re.compile(
            r'[A-Za-z0-9-\._]+(@| at | \[at\] |\[at\]| \(at\) |\(at\)| @ | \-at\- |<at>)(([a-z0-9\-]+)(\.| dot | \. | \[dot\] |\(dot\)|<dot>))+([a-z]+)')
        rough_match = rough_pattern.finditer(content)
        for rm in rough_match:
            pattern = re.compile(
                r'(([A-Za-z0-9-_]+)(\.| dot | \. )?)+(@| at | \[at\] |\[at\]| \(at\) |\(at\)| @ | \-at\- |<at>)(([a-z0-9\-]+)(\.| dot | \. | \[dot\] |\(dot\)|<dot>))+([a-z]+)')
            match = pattern.finditer(rm.group())
            for m in match:
                emails.append(
                    m.group().lower().replace(' dot ', '.').replace('(dot)', '.').replace(' at ', '@').replace('[at]',
                                                                                                               '@').replace(
                        '(at)', '@').replace(
                        '(@)', '@').replace(' [dot] ', '.').replace('<dot>', '.').replace('<at>', '@').replace('--@--',
                                                                                                               '@').replace(
                        '-at-', '@').replace(' ', ''))
        return emails

    def filt_email(self,snippets):

        def efilter(snippet):
            snippet['emails'] = self.match_emails(snippet["content"])
            return snippet

        snippets = [efilter(s) for s in snippets]
        snippets = [s for s in snippets if s['emails']]
        return snippets

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


    def cal_sparse_tf_idf(corpus,test_corpus):
        vectorizer=CountVectorizer()
        transformer=TfidfTransformer()
        tfidf=transformer.fit_transform(corpus)
        test_tf=vectorizer.transform(test_corpus)
        test_tf_idf=transformer.transform(test_tf)

    #crawl main page of person
    def match_page(self, snippet, person, pos):
        keywords_names=snippet['h_keywords']
        keywords_orgs=snippet['h_keywords']
        sim_arr_name=[0]
        for k_n in set(keywords_names):
            sim_arr_name.append(chinese_helper.simila_name(k_n,person['name_zh'] if 'name_zh' in person else person['name']))
        sim_nam=max(sim_arr_name)
        sim_arr_org = [0]
        for k_n in set(keywords_orgs):
            org=person['simple_affiliation']
            sim_arr_org.append(chinese_helper.simila_name(k_n,org))
        sim_org= max(sim_arr_org)
        logger.info("%f--%f"%(sim_nam,sim_org))
        if sim_nam>0.3 and sim_org>=0:
            if ''.join(person['simple_affiliation']).find("公司")==-1:
                if snippet['title'].find("主页")!=-1 or snippet['title'].find("个人")!=-1 or snippet['title'].find("介绍")!=-1:
                    if snippet['title'].find(person['name'])!=-1:
                        if snippet['page_src'].find('baike.baidu.com')!=-1:
                            snippet['importance']=0.5*sim_nam+0.5*sim_org+1/(pos+2)+0.2+0.5+0.5
                        else:
                            snippet['importance'] = 0.5 * sim_nam + 0.5 * sim_org  + 1 / (pos + 2) + 0.2 + 0.5
                    else:
                        snippet['importance'] = 0.5 * sim_nam + 0.5 * sim_org  + 1 / (pos + 2) + 0.2
                else:
                    if snippet['title'].find(person['name']) != -1:
                        if snippet['page_src'].find('baike.baidu.com') != -1:
                            snippet['importance'] = 0.5 * sim_nam + 0.5 * sim_org  + 1 / (
                            pos + 2)  + 0.5 + 0.5
                        else:
                            snippet['importance'] = 0.5 * sim_nam + 0.5 * sim_org + 1 / (pos + 2) + 0.5
                    else:
                        snippet['importance'] = 0.5 * sim_nam + 0.5 * sim_org +  + 1 / (pos + 2)
            else:
                if snippet['title'].find("高管")!=-1:
                    snippet['importance']=0.5+1/(pos+2)
            return snippet

    def match_page_simple(self,snippet,person,pos):
        score=0
        if snippet['title'].find(person['name']) !=-1:
            score=score+0.5
        if snippet['title'].find(person['simple_affiliation'])!=-1:
            score=score+0.5
        if snippet['content'].find(person['name'])!=-1:
            score=score+0.5
        if snippet['content'].find(person['simple_affiliation'])!=-1:
            score=score+0.5
        if snippet['page_src'].find('baike.baidu.com') != -1:
            score=score+0.2
        score+=1/(pos+2)
        snippet['importance']=score
        return snippet
    def filt_page(self,snippets,person):
        def filter(snippet,pos):
            return self.match_page_simple(snippet,person,pos)
        snippets=[filter(s,pos) for pos,s in enumerate(snippets)]
        snippets=[s for s in snippets if s is not None and 'importance' in s]
        return sorted(snippets,key=lambda s:s['importance'],reverse=True)

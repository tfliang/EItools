import bs4
import re
import requests

from EItools.client.mongo_client import MongoDBClient
from EItools.classifier_mainpage.Str2Query import Str2Query
from MagicGoogle import MagicGoogle
from MagicBaidu import MagicBaidu
from EItools.classifier_mainpage.Feature import Feature
from sklearn.externals import joblib

from EItools.config.globalvar import CLASSIFIER_DIR
from EItools.log.log import logger
from EItools.extract.interface import interface

clf = joblib.load(CLASSIFIER_DIR + '/data/classifier.pkl')

PROXIES = [{
    'http': 'http://127.0.0.1:8123',
    'https': 'https://127.0.0.1:8123'
}]

mg = MagicGoogle(PROXIES)
mb = MagicBaidu()


def get_res(query):
    res = []
    try:
        for i in mg.search(query=query, pause=0.5):
            try:
                th = {}
                for k in i:
                    if i[k] is None:
                        th[k] = ''
                    else:
                        th[k] = i[k]
                th['source'] = 'google'
                th['label'] = clf.predict_proba([Feature.get_feature(query, th)])[0][1]
                res.append(th)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    try:
        for i in mb.search(query=query, pause=0.5):
            try:
                th = i
                th['source'] = 'baidu'
                th['url'] = i['url']
                th['label'] = clf.predict_proba([Feature.get_feature(query, th)])[0][1]
                res.append(th)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    return res


def Get(str):
    query = Str2Query.get_query(str)
    cra = {}
    cra['ini'] = str
    cra['query'] = query
    cra['res'] = get_res(query)
    return cra


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'
}


def get_content(url, headers):
    '''''
    @获取403禁止访问的网页
    '''
    res = requests.get(url, headers=headers)
    # res.encoding='utf-8'
    content = res.content
    return content


def get_main_page(url, person):
    try:
        print(url)
        source_code = get_content(url, headers)
        soup = bs4.BeautifulSoup(source_code, 'html.parser')
        # scripts = soup.find_all(name='div', attrs={
        #     "class": re.compile(r'.*(foot|nav|Nav|footer|bottom|pageR_t clearfix|menu|header).*$')})
        # scriptsId = soup.find_all(name='div', attrs={
        #     "id": re.compile(r'.*(foot|nav|Nav|footer|bottom|pageR_t clearfix|header|guest|head).*$')})
        # for script in scripts + scriptsId:
        #     script.extract()
        for script in soup(["script", "style"]):
            script.extract()
        text=soup.get_text()
        p_text=re.split('\n',text)
        # p_text=[]
        # texts = soup.find_all('p')
        # for text in texts:
        #     p_text.append(text.get_text())
        #     for t in text.splitlines():
        #         if
        # lines = (line.strip() for line in text.splitlines())
        # text = '\n\r'.join(chunk for chunk in lines if chunk)

        PER_list=[]
        ADR_list=[]
        AFF_list=[]
        TIT_list=[]
        JOB_list=[]
        DOM_list=[]
        EDU_list=[]
        WRK_list=[]
        SOC_list=[]
        AWD_list=[]
        PAT_list=[]
        PRJ_list=[]
        for t in p_text:
            if t is not None and t!='':
                print(t)
                result=interface(t)
                PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ = result if result is not None else (
            None, None, None, None, None, None, None, None, None, None, None, None)
                PER_list.append(PER)
                ADR_list.append(ADR)
                AFF_list.append(AFF)
                TIT_list.append(TIT)
                JOB_list.append(JOB)
                DOM_list.append(DOM)
                EDU_list.append(EDU)
                WRK_list.append(WRK)
                SOC_list.append(SOC)
                AWD_list.append(AWD)
                PAT_list.append(PAT)
                PRJ_list.append(PRJ)
        p_new={}
        p_new['_id']=person['_id']
        p_new['url']=url
        p_new['ini']=person['ini']
        p_new['PER']=PER_list
        p_new['ADR']=ADR_list
        p_new['AFF']=AFF_list
        p_new['TIT']=TIT_list
        p_new['JOB']=JOB_list
        p_new['DOM']=DOM_list
        p_new['EDU']=EDU_list
        p_new['WRK']=WRK_list
        p_new['SOC']=SOC_list
        p_new['AWD']=AWD_list
        p_new['PAT']=PAT_list
        p_new['PRJ']=PRJ_list
        mongo_client.db['crawled_test'].save(p_new)
        # lines = (line.strip() for line in text.split())
        # if person['ini'].find("公司") != -1:
        #     text = '<k>'.join(chunk for chunk in lines if chunk.find(person['ini'].split()[0]) != -1)
        # else:
        #     text = '<k>'.join(chunk for chunk in lines if chunk)
    except Exception as e:
        logger.info(e)
        text = ""
    return text

def get_main_page_simple(url, person):
    try:
        print(url)
        source_code = get_content(url, headers)
        soup = bs4.BeautifulSoup(source_code, 'html.parser')
        # scripts = soup.find_all(name='div', attrs={
        #     "class": re.compile(r'.*(foot|nav|Nav|footer|bottom|pageR_t clearfix|menu|header).*$')})
        # scriptsId = soup.find_all(name='div', attrs={
        #     "id": re.compile(r'.*(foot|nav|Nav|footer|bottom|pageR_t clearfix|header|guest|head).*$')})
        # for script in scripts + scriptsId:
        #     script.extract()
        for script in soup(["script", "style"]):
            script.extract()
        text=soup.get_text()
        lines = (line.strip() for line in text.split())
        if person['ini'].find("公司") != -1:
            text = ' '.join(chunk for chunk in lines if chunk.find(person['ini'].split()[0]) != -1)
        else:
            text = ' '.join(chunk for chunk in lines if chunk)
        print(text)
    except Exception as e:
        logger.info(e)
        text = ""
    interface(text)
    return text

mongo_client = MongoDBClient()


def crawl_person(offset, size):
    persons = mongo_client.db['search3'].find().skip(offset).limit(size)
    for i, p in enumerate(persons):
        mongo_client.db['search'].save(p)
        if i >= 0 and i < size:
            if 'status' not in p or p['status'] != 0:
                print("{}-{}".format(i, p['_id']))
                # name = p['name']
                # org = p['org']
                # str = '{},{}'.format(name, org)
                query = Str2Query.get_query(p['ini'])
                result = get_res(p['res'])
                result = p['res']
                result_with_label = []
                for i, th in enumerate(result):
                    th['label'] = clf.predict_proba([Feature.get_feature(query, th)])[0][1]
                    result[i] = th
                    result_with_label.append(th)
                mongo_client.db['search'].update({"_id": p['_id']}, {"$set": {"res": result_with_label}})
                result_sorted = sorted(result, key=lambda s: s['label'], reverse=True)
                if len(result_sorted) > 0:
                    p['url'] = result_sorted[0]['url']
                    p['source'] = 'crawler'
                    p['info'] = get_main_page(p['url'], p)
                mongo_client.db['crawled_person_final'].save(p)
                mongo_client.db['search'].update({"_id": p['_id']}, {"$set": {"status": 0}})

def test_data():
    persons=mongo_client.db['crawled_person_final'].find().skip(0).limit(100)
    for p in persons:
        if 'url' in p:
            get_main_page(p['url'],p)


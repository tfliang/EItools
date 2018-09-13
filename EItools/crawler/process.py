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
    'http': 'http://159.203.174.2:3128'
    # 'http':'http://127.0.0.1:8123',
    # 'https':'http://127.0.0.1:8123'
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
                th['label'] = int(clf.predict([Feature.get_feature(query, th)])[0])
                th['score']=clf.predict_proba([Feature.get_feature(query, th)])[0][1]
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
                th['label'] = int(clf.predict([Feature.get_feature(query, th)])[0])
                th['score']=clf.predict_proba([Feature.get_feature(query, th)])[0][1]
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




import bs4
import re
import requests

from EItools.magic_search import MagicSearch
from EItools.client.mongo_client import MongoDBClient
from EItools.classifier_mainpage.Str2Query import Str2Query

from EItools.classifier_mainpage.Feature import Feature
from sklearn.externals import joblib

from EItools.config.globalvar import CLASSIFIER_DIR
from EItools.log.log import logger
from EItools.extract.interface import interface

clf = joblib.load(CLASSIFIER_DIR + '/data/classifier.pkl')

PROXIES = [{
    #'http': 'http://159.203.174.2:3128'
    'http':'http://127.0.0.1:8123',
    'https':'http://127.0.0.1:8123'
}]

ms = MagicSearch(PROXIES)
def get_res(query):
    res = []
    try:
        for i in ms.search(query=query, pause=0.5):
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
        for i in ms.search_baidu(query=query, pause=0.5):
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






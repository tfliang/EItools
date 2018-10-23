import random

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
from EItools.classifier_mainpage.Name import Name
from EItools.magic_search.magic_search import magic_search

clf = joblib.load(CLASSIFIER_DIR + '/data/classifier.pkl')

ms = magic_search
def get_res(fakequery, query):
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
                th['label'] = int(clf.predict([Feature.get_feature(fakequery, th)])[0])
                th['score'] = clf.predict_proba([Feature.get_feature(fakequery, th)])[0][1]
                res.append(th)
            except Exception as e:
                logger.error("when search google:{}".format(e))
    except Exception as e:
        print(e)
    try:
        for i in ms.search_baidu(query=query, pause=0.5):
            try:
                th = i
                th['source'] = 'baidu'
                th['url'] = i['url']
                th['label'] = int(clf.predict([Feature.get_feature(fakequery, th)])[0])
                th['score'] = clf.predict_proba([Feature.get_feature(fakequery, th)])[0][1]
                res.append(th)
            except Exception as e:
                logger.error("when search baidu:{}".format(e))
    except Exception as e:
        print(e)
    return res

def Get_all(str):
    name, aff = Str2Query.get_query(str)
    cra = {}
    cra['ini'] = str
    fakequery = name + ' ' + aff
    if aff.find('中国科学院') != -1 or aff.find('中科院') != -1:
        cra['type'] = 'cas.cn'
        # if Name.iscommon(name):
        query = ' '.join([name, "中国科学院",' .cas.cn',' baidu.com'])
    # else:
    #	query = ' '.join([name, 'site:*.cas.cn'])
    elif aff.find('大学') != -1 or aff.find('学院') != -1:
        cra['type'] = 'edu.cn'
        if Name.iscommon(name):
            query = ' '.join([name, aff, ' .edu.cn', ' baidu.com'])
        else:
            query = ' '.join([name, ' .edu.cn', ' baidu.com'])
    else:
        cra['type'] = 'other'
        query = ' '.join([name, aff])
    cra['query'] = query
    cra['res'] = get_res(fakequery, query)
    ok = False
    for d in cra['res']:
        # print(d['title'], d['label'])
        # input()
        if d['label'] > 0.7:
            ok = True
            break
    if (not ok) and cra['type'] != 'other':
        cra['query'] = fakequery
        cra['type'] = 'other'
        cra['res'] = get_res(fakequery, fakequery)
    return cra


def Get(str):
    # query = Str2Query.get_query(str)
    # cra = {}
    # cra['ini'] = str
    # cra['query'] = query
    # cra['res'] = get_res(query)
    # return cra
    name, aff = Str2Query.get_query(str)
    cra = {}
    cra['ini'] = str
    fakequery = name + ' ' + aff
    if aff.find('中国科学院') != -1 or aff.find('中科院') != -1:
        cra['type'] = 'cas.cn'
        # if Name.iscommon(name):
        query = ' '.join([name, "中国科学院","site.*.cas.cn","site.*.ac.cn"])
    # else:
    #	query = ' '.join([name, 'site:*.cas.cn'])
    elif aff.find('大学') != -1 or aff.find('学院') != -1:
        cra['type'] = 'edu.cn'
        if Name.iscommon(name):
            query = ' '.join([name, aff, 'site.*.edu.cn'])
        else:
            query = ' '.join([name, 'site.*.edu.cn'])
    else:
        cra['type'] = 'other'
        query = ' '.join([name, aff])
    cra['query'] = query
    cra['res'] = get_res(fakequery, query)
    ok = False
    for d in cra['res']:
        # print(d['title'], d['label'])
        # input()
        if d['label'] > 0.7:
            ok = True
            break
    if (not ok) and cra['type'] != 'other':
        cra['query'] = fakequery
        cra['type'] = 'other'
        cra['res'] = get_res(fakequery, fakequery)
    return cra

#






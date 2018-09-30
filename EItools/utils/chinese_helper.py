import hashlib
import urllib
import json
from urllib import request
import random
import jieba
import jieba.posseg as pseg
import re

from idna import unichr

from EItools.utils.edit_distance import EditDistance

APP_ID = '20170228000040045'
SECRET_KEY = 'SxYBqtNq6V4JehH_JmBy'
URL = 'https://api.fanyi.baidu.com/api/trans/vip/translate'

def translate(q,fromLang,toLang):
    salt = random.randint(32768, 65536)
    sign = APP_ID + q + str(salt) + SECRET_KEY
    m1 = hashlib.md5()
    m1.update(sign.encode(encoding='utf-8', errors='strict'))
    sign = m1.hexdigest()
    myurl = URL + '?appid=' + APP_ID + '&q=' + urllib.request.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign
    try:
        response = request.urlopen(myurl)
        result=response.read().decode('utf-8')
        result=json.loads(result)
        return result['trans_result'][0]['dst']
    except Exception as e:
        print(e)

ZH_PATTERN = re.compile(u'[\u4e00-\u9fa5]+')

def contain_zh(word):
    global ZH_PATTERN
    match = re.search(ZH_PATTERN,word)
    if match:
        return True
    else:
        return False

#词性标注，nr为人名
def get_first_name(messageContent):
    words = pseg.cut(messageContent)
    for word, flag in words:
        if flag == 'nr'and len(word)>1:#单字姓名去掉
            return word

    return False

def get_all_words(messageContent,p="nr"):
    words = pseg.cut(messageContent)
    ks = []
    for word, flag in words:
        print(word+"  "+flag)
        ks.append(word)
    return list(set(ks))

#修改停用词集合中所有词性为名词，大部分为名词
def alter_word_tag_toX(list):
    for x in list:
        jieba.add_word(x, tag='n')

def load_stop_word(StopWordFileName):
    stop_word_file = open(StopWordFileName, 'r', encoding='utf-8')
    stop_word_list = []

    for line in stop_word_file.readlines():
        stop_word_list.append(line.strip('\n'))

    set(stop_word_list)
    stop_word_file.close()
    alter_word_tag_toX(stop_word_list)

def recognize_keywords(content,p="nr"):
    #jieba.enable_parallel(3)
    words = get_all_words(content,p)
    return words


def is_null_or_blank(s):
    return s is None or s==""

regexPunctuations = "[\\pP‘’“”$^~+=\\|<>`]"


def simila_name(nl,nr):
    nl=nl.replace(' ','')
    nr=nr.replace(' ','')
    print("%s--%s"%(nl,nr))
    escapeStr=["et","al","etc"]
    def trans(name):
        if contain_zh(name):
            name = translate(name, 'zh', 'en')
        else:
            name = translate(name, 'en', 'en')
        return name
    if is_null_or_blank(nl) or is_null_or_blank(nr):
        return 0.1
    else:
        if nl==nr:
            return 1.0
        nl_l=contain_zh(nl)
        nr_l=contain_zh(nr)
        if nl_l!=nr_l:
            if nl_l:
                nl=trans(nl)
            else:
                nr=trans(nr)
        nl=nl.lower()
        nr=nr.lower()
        if nl==nr:
            return 1.0
        else:
            def filt(s):
                return not (s is None or s == "") and not (s in escapeStr)
            def nameStr2Arr(ns):
                return list(filter(filt,ns.replace(regexPunctuations," ").lower().split(" ")))
            def contain_each(sarr,darr):
                for s in sarr:
                    if s not in darr:
                        return False
                return True
            nlarr=nameStr2Arr(nl)
            nrarr=nameStr2Arr(nr)
            e = EditDistance()
            flag=False
            for la in nlarr:
                for ra in nrarr:
                    if e.minDistance(la,ra)<2:
                        flag=True
                        if (contain_each(nlarr,nrarr) or contain_each(nrarr,nlarr)):
                            return 0.7
                        else:
                            return 0.3
            if not flag:
                if contain_each(nlarr, nrarr) or contain_each(nrarr, nlarr):
                    return 0.5
                else:
                    return 0


# -*- coding: cp936 -*-
def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += unichr(inside_code)
    return rstring


def strB2Q(ustring):
    """半角转全角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 32:  # 半角空格直接转化
            inside_code = 12288
        elif inside_code >= 32 and inside_code <= 126:  # 半角字符（除空格）根据关系转化
            inside_code += 65248

        rstring += unichr(inside_code)
    return rstring










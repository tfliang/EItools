#coding=utf-8
import heapq
import json

import re

import jieba
import requests
import tensorflow as tf
import time

from bs4 import BeautifulSoup
from bson import ObjectId

from EItools.classifier_mainpage.Extract import Extract
from EItools.client.mongo_client import MongoDBClient
from EItools.extract.interface import extract_one_3, print_tag, interface, extract_project, extract_patent, \
    extract_award
from EItools.log.log import logger
from EItools.utils import chinese_helper


def find_aff(text):
    tf.reset_default_graph()
    result = extract_one_3(text)
    PER, ADR, AFF = result if result is not None else (None, None, None)
    if PER is not None:
        print_tag(PER, 'PER', text)
    if ADR is not None:
        print_tag(ADR, 'ADR', text)
    if AFF is not None:
        print_tag(AFF, 'AFF', text)
    return AFF
def find_name(text):
    tf.reset_default_graph()
    result = extract_one_3(text)
    PER, ADR, AFF = result if result is not None else (None, None, None)
    if PER is not None:
        print_tag(PER, 'PER', text)
    if ADR is not None:
        print_tag(ADR, 'ADR', text)
    if AFF is not None:
        print_tag(AFF, 'AFF', text)
    return PER
patent_time=r'((?:19|20)[0-9]{2})[年|.|/]?'
pattern_time = r'((?:19|20)[0-9]{2}[年|.|/]?[0-9]{0,2}[月]?|至今|今)'
pattern_work_time=r'(曾任|现任|现为|同年|(?:19|20)[0-9]{2}[年./-]?[0-9]{0,2}(月|.)?\s*(?:-|－|—|--|-|～|--|毕业|至|~)+\s*(?:(?:(?:19|20)[0-9]{2}[年|.|/|-]?[0-9]{0,2}[月]?)|至今|今|现在)?)'

def match(aff_list,time_list,text):
    aff_list_with_index=zip(aff_list,[text.index(aff) for aff in aff_list])
    time_list_with_index=zip(time_list,[text.index(time) for time in time_list])
    aff_list_with_index=sorted(zip([text.index(aff) for aff in aff_list],aff_list) ,key=lambda a:a[0])
    time_list_with_index=sorted(zip(time_list,[text.index(time) for time in time_list]),key=lambda a:a[0])
    if len(aff_list_with_index)==len(time_list_with_index):
        for i,(index,aff) in enumerate(aff_list_with_index):
            yield(time_list_with_index[i][1],aff_list_with_index[i][1])
    elif len(aff_list_with_index)!=len(time_list_with_index):
        i=0
        j=0
        while i!=len(time_list_with_index) and j!=len(aff_list_with_index):
            if time_list_with_index[i]<aff_list_with_index[j]<time_list_with_index[i+1]:
                yield (time_list_with_index[i][1],aff_list_with_index[j][1])
                j=j+1
            else:
                yield (time_list_with_index[i+1][1],aff_list_with_index[j][1])
                i=i+1
                j=j+1

#国务院学位委员会学科评议组(化学组)成员
def is_soc_aff(text):
    pat = re.compile('编辑|本站不保证|万元|基金|项目|专利')
    if len(pat.findall(text)) != 0:
        return False
    return True
def find_soc(text):
    is_contain_en=re.compile(r'[A-Za-z]',re.S)
    match=re.findall(is_contain_en,text)
    time = re.findall(pattern_time, text)
    text = re.sub(pattern_time, '', text)
    titles=Extract.extract_soc_position(text)
    title=""
    if titles is not None and len(titles)>0:
        title=' '.join(titles)
        for title in titles:
            text=text.replace(title,',')
        text = re.sub(r'[,，、。.-]', '', text)
    aff=text
    academic_org_exp = None
    if  aff != "" and is_soc_aff(aff) and title!="":
        if len(time) >= 2:
            academic_org_exp = {"title": title, "org": aff, "duration": '-'.join(time)}
        elif len(time) == 1:
            academic_org_exp = {"title": title, "org": aff, "duration": time[0]}
        else:
            academic_org_exp = {"title": title, "org": aff, "duration": ""}

    return academic_org_exp

def find_word_en(text):
    match_data=re.findall('[a-zA-Z]',text)
    part_en=''.join(match_data)
    return len(part_en)/len(text)>0.5

#1985.7 南开大学研究生
def find_work(text):
    if find_word_en(text):
        text=chinese_helper.translate(text)
    aff_list = find_aff(text)

    time = re.findall(pattern_time, text)
    # if len(time_all)>0:
    #     time=re.split(r'[年./]',time_all[0])
    # else:
    #     time=[]
    if aff_list is not None and len(aff_list) > 0:
        #aff = aff_list[0]
        aff_all=",".join(aff_list)
        #title = text[text.index(aff) + len(aff):]
        text=re.sub(pattern_time,'',text)
        position=""
        for aff in aff_list:
            text=text.replace(aff,',')
        text=re.sub(r'[,，、。.-]','',text)
        position=','.join(Extract.extrac_position(text))
        print("time is:{}".format(time))
        print("aff is:{}".format(aff_all))
        print("positon is:{}".format(position))
        exp = None
        if len(time) >= 2:
            exp = {"start": time[0], "end": time[1], "position": position,"inst": aff_all}
        elif len(time) == 1:
            exp = {"start": time[0], "position": position,"inst": aff_all}
        elif len(time) == 0:
            exp = {"position": position,"inst": aff_all}
        return exp


#1981年本科毕业于湖南师范大学化学系
def find_edu(text):
    aff_list = find_aff(text)

    time = re.findall(pattern_time, text)

    if aff_list is not None and len(aff_list) > 0:
        aff_all = ','.join(aff_list)
        for aff in aff_list:
            rest_content = text.replace(aff,'',)
    else:
        rest_content=text
    try:
        degree=""
        diploma=""
        if '本科' in rest_content or '学士' in rest_content:
            degree='学士'
        if '研究生' in rest_content or '硕士' in rest_content :
            degree='硕士'
        if '博士' in rest_content or '博士后' in rest_content:
            degree='博士'
        if degree=='学士':
            diploma='本科'
        elif degree=='博士' or degree=='硕士':
            diploma='研究生'
        print("time is:{}".format(time))
        print("aff is:{}".format(aff))
        print("degree is:{}".format(degree))
        print("diploma is:{}".format(diploma))

        edu_exp = None
        if  degree !="" or aff_all!="":
            if len(time) >= 2:
                edu_exp = {"start":time[0] ,"end":time[1], "diploma": diploma, "degree": degree,"inst":aff_all}
            elif len(time) == 1:
                edu_exp ={"end":time[0],"diploma": diploma, "degree": degree,"inst":aff_all}
            elif len(time) == 0:
                edu_exp = {"diploma": diploma, "degree": degree,"inst":aff_all}
        return edu_exp
    except Exception as e:
        logger.info("when extract education info:{}".format(e))
        return None


def find_patent(text):
    text=re.sub(' ','',text)
    inventor_names=find_name(text)
    patent_number_pattern=r'((?:ZL|CN|JP)?[0-9X\\s.]{7,15}.{0,1}[0-9X]{0,1})'
    patent_number=re.findall(patent_number_pattern,text)
    text = re.sub(patent_number_pattern, "", text)
    tf.reset_default_graph()
    patent_name=extract_patent(text)
    patent_name=''.join(patent_name) if patent_name is not None else ""
    time = re.findall(patent_time, text)
    print("time is:{}".format(time))
    print("inventor is:{}".format(inventor_names))
    print("patent_number is:{}".format(patent_number))
    print("patent_name is:{}".format(patent_name))
    patent=None
    if len(time)>=2:
        patent = {"inventor_names":','.join(inventor_names) if inventor_names is not None else "","code":''.join(patent_number) if patent_number is not None else "" ,"issue_date":time[0] if time is not None and len(time)>0 else "","issue_by":"","title":patent_name}
    elif len(time)==1:
        patent = {"inventor_names":','.join(inventor_names) if inventor_names is not None else "","code":''.join(patent_number) if patent_number is not None else "" ,"issue_date":time[0] if time is not None and len(time)>0 else "","issue_by":"","title":patent_name}
    elif len(time)==0:
        patent = {"inventor_names":','.join(inventor_names) if inventor_names is not None else "","code":''.join(patent_number) if patent_number is not None else "" ,"issue_date":time[0] if time is not None and len(time)>0 else "","issue_by":"","title":patent_name}
    return patent

def find_project(text):
    if len(text)<5:
        return None
    project_number=re.findall(r'[0-9a-zA-Z]{6,}',text)
    text=re.sub(r'[0-9a-zA-Z]{6,}',"",text)
    time=re.findall(pattern_time,text)
    project_funds=re.findall(r'[\d]+[万元]+',text)
    tf.reset_default_graph()
    result=extract_project(text)
    project_cat,project_name= result if result is not None else (None,None)
    print("number is:{}".format(project_number))
    print("funds is:{}".format(project_funds))
    print("project name is:{}".format(project_name))
    print("project cat is:{}".format(project_cat))
    print("project time is:{}".format(time))
    project_name=''.join(project_name) if project_name is not None else""
    project_cat=''.join(project_cat) if project_cat is not None else ""
    project_funds=''.join(project_funds) if project_funds is not None else ""
    project_number=''.join(project_number)
    project=None
    if project_name=="" and project_cat=="":
        return project
    if len(time)>=2:
        project={"title":project_name,"cat":project_cat,"fund":project_funds,"start":time[0],"end":time[1],"role":"","code":project_number}
    elif len(time)==1:
        project = {"title": project_name, "cat": project_cat, "fund": project_funds, "start": time[0],"end":"","role":"","code":project_number}
    elif len(time)==0:
        project = {"title": project_name, "cat": project_cat, "fund": project_funds,"start":"","end":"","role":"","code":project_number}
    return project

def find_award(text):
    time=re.findall(pattern_time,text)
    tf.reset_default_graph()
    result = extract_award(text)
    award_name, award_title = result if result is not None else (None, None)
    # title_all=re.findall(r'(国家|省|市|自治区|政府|协会|学会|国务院)[\u4e00-\u9fa5]*?(科学|技术|进步|自然|发明|科技){1,}\s*?奖',text)
    #title=title_all[0] if len(title_all)>0  else ""
    time= time[0] if len(time)>0 else ""
    name=','.join(award_name) if award_name is not None else ""
    title=','.join(award_title) if award_title is not None else ""
    awards=[]
    if title=="" and name=="":
        return name
    if title!=""  or name !="":
        if len(award_title)>1:
            for a_t in award_title:
                award = {'title': a_t, 'year': time, 'award': ""}
                awards.append(award)
        else:
            award = {'title': title, 'year': time, 'award': name}
            awards.append(award)
    return awards

def find_socs(text):
    socs=[]
    socs_all = []
    # datas = re.findall(pattern_work_time, text)
    # if len(datas) > 0:
    #     indexs = [m.span()[0] for m in re.finditer(pattern_work_time, text)]
    #     socs_all = [text[indexs[i]:indexs[i + 1]] for i, data in enumerate(indexs) if i < len(indexs) - 1]
    #     if len(text[0:indexs[0]]) > 3:
    #         socs_all.append(text[0:indexs[0]])
    #     socs_all.append(text[indexs[len(indexs) - 1]:len(text)])
    # if len(socs_all) == 0:
    socs_all = re.split(r'[。\n,，；;、]', text)
    for t in socs_all:
        if t!="":
            soc=find_soc(t)
            if soc is not None:
                socs.append(soc)
    return socs


def find_works(text):
    works=[]
    datas = re.findall(pattern_work_time, text)
    works_all=[]
    if len(datas) > 0:
        indexs = [m.span()[0] for m in re.finditer(pattern_work_time, text)]
        works_all = [text[indexs[i]:indexs[i + 1]] for i, data in enumerate(indexs) if i < len(indexs) - 1]
        if len(text[0:indexs[0]]) > 3:
            works_all.append(text[0:indexs[0]])
        works_all.append(text[indexs[len(indexs) - 1]:len(text)])
    if len(works_all)==0:
        works_all=re.split(r'[。\n；;]', text)
    for t in list(set(works_all)):
        if t!="":
            work=find_work(t)
            if work is not None:
                works.append(work)
    return works

def find_edus(text):
    edus=[]
    datas =[m.group() for m in re.finditer(pattern_work_time,text)]
    edus_all = []
    if len(datas) > 0:
        indexs = [m.span()[0] for m in re.finditer(pattern_work_time,text)]
        edus_all = [text[indexs[i]:indexs[i + 1]] for i, d in enumerate(indexs) if i < len(indexs) - 1]
        if len(text[0:indexs[0]]) > 3:
            edus_all.append(text[0:indexs[0]])
        edus_all.append(text[indexs[len(indexs) - 1]:len(text)])
    if len(edus_all) == 0:
        edus_all = re.split(r'[。\n；;]', text)
    print(edus_all)
    for t in list(set(edus_all)):
        if t!="":
            edu=find_edu(t)
            if edu is not None:
                edus.append(edu)
    return edus


def find_patents(text):
    patents=[]
    #sequence_pattern='(\d[．.、]\s*[\u4e00-\u9fa5]+)'
    #sequence_pattern_second='([(【[（]?\d\s*[)）]】?\s*[\u4e00-\u9fa5])'
    #datas = [m.group() for m in re.finditer(sequence_pattern_second, text)]
    #indexs = [m.span()[0] for m in re.finditer(sequence_pattern_second,text)]
    #if len(datas) == 0:
        #datas = [m.group() for m in re.finditer(sequence_pattern, text)]
        #indexs = [m.span()[0] for m in re.finditer(sequence_pattern, text)]
    #patents_all = []
    #if len(datas) > 0:
         #patents_all = [text[indexs[i]:indexs[i + 1]] for i, d in enumerate(indexs) if i < len(indexs) - 1]
         #if len(text[0:indexs[0]])>3:
            #patents_all.append(text[0:indexs[0]])
         #patents_all.append(text[indexs[len(indexs) - 1]:len(text)])
    # patents_all = find_sentence(text)
    # if len(patents_all) == 0:
    patents_all = re.split(r'[\n]', text)
    print(patents_all)
    for t in patents_all:
        if t!="":
            patent=find_patent(t)
            tf.reset_default_graph()
            if patent is not None:
                patents.append(patent)
    return patents


def find_projects(text):
    projects=[]
    # text_trans = re.sub(r'[0-9a-zA-Z]{6,}', "*", text)
    #text_trans = re.search(pattern_work_time,"*",text)
    # print(text_trans)
    # sequence_pattern = r'(\d[．.、]+\s*[\u4e00-\u9fa5]+)'
    # sequence_pattern_second = r'([(【[（]?\d\s*[)）]】?\s*[\u4e00-\u9fa5]?)'
    # '[\d\s*]?\s*'
    # datas = [m.group() for m in re.finditer(sequence_pattern, text)]
    # indexs = [m.span()[0] for m in re.finditer(sequence_pattern, text)]
    # if len(datas) == 0:
    #     datas = [m.group() for m in re.finditer(sequence_pattern_second, text)]
    #     indexs = [m.span()[0] for m in re.finditer(sequence_pattern_second, text)]
    # projects_all = []
    # if len(datas) > 0:
    #     projects_all = [text[indexs[i]:indexs[i + 1]] for i, data in enumerate(indexs) if i < len(indexs) - 1]
    #     if len(text[0:indexs[0]]) > 3:
    #         projects_all.append(text[0:indexs[0]])
    #     projects_all.append(text[indexs[len(indexs) - 1]:len(text)])
    projects_all=[]
    #projects_all=find_sentence(text)
    if len(projects_all) <= 1:
        if '。' in text:
            projects_all = re.split(r'[。]', text)
        if '；' in text:
            projects_all=re.split(r';',text)
        else:
            projects_all = re.split(r'[\n]', text)
    print(projects_all)
    for t in projects_all:
        if t!="":
            project=find_project(t)
            if project is not None:
                projects.append(project)
    return projects

def find_awards(text):
    awards=[]
    # sequence_pattern = r'(\d[．.、]+\s*[\u4e00-\u9fa5]+)'
    # sequence_pattern_second = r'([(【[（]?\d\s*[)）]】?\s*[\u4e00-\u9fa5]?)'
    # '[\d\s*]?\s*'
    # datas = [m.group() for m in re.finditer(sequence_pattern, text)]
    # indexs = [m.span()[0] for m in re.finditer(sequence_pattern, text)]
    # if len(datas) == 0:
    #     datas = [m.group() for m in re.finditer(sequence_pattern_second, text)]
    #     indexs = [m.span()[0] for m in re.finditer(sequence_pattern_second, text)]
    # awards_all=[]
    # if len(datas)>0:
    #     awards_all=[text[indexs[i]:indexs[i+1]] for i,data in enumerate(indexs) if i<len(indexs)-1]
    #     if len(text[0:indexs[0]]) > 3:
    #         awards_all.append(text[0:indexs[0]])
    #     awards_all.append(text[indexs[len(indexs)-1]:len(text)])
    #awards_all=find_sentence(text)
    #if len(awards_all)==0:
    awards_all=re.split(r'[\n]', text)
    print(awards_all)
    for t in awards_all:
        if t!="":
            award=find_award(t)
            if award is not None:
                for a in award:
                    awards.append(a)
    return awards

def find_awards_list(awd_list):
    awd_aparts=[]
    if awd_list is not None:
        for awd in awd_list:
            awd_apart=find_awards(awd)
            for a in awd_apart:
                awd_aparts.append(a)
    return awd_aparts


def find_sentence(s):
    now = 1
    tj = {']': 0, ')': 0, '.': 0 }
    res = {']': [], ')': [], '.': []}
    for k in tj:
        now = 0
        last = 0
        first=True
        while True:
            mats = '%d\s*\\%s' % (now + 1, k)
            mat = re.search(mats, s[last:])
            if now==2:
                print(2)
            if mat is None:
                # res[k].append(s[last:].find('\n')) # 丢掉了最后一条
                if first:
                    first=False
                    now+=1
                    mats = '%d\\%s' % (now + 1, k)
                    mat = re.search(mats, s[last:])
                    if mat is None:
                        now +=1
                        mats = '%d\\%s' % (now + 1, k)
                        mat = re.search(mats, s[last:])
                        if mat is None:
                            break
                else:
                    break
            last += mat.start()
            res[k].append(mat.start())
            now += 1
        tj[k] = now
    print(res)
    mac = ''
    ma = 0
    for k in tj:
        if tj[k] > ma:
            ma = tj[k]
            mac = k
    print(tj)
    print(ma, mac)
    paper = []
    for i in range(0, len(res[mac])):
        paper.append(s[:res[mac][i]])
        s = s[res[mac][i]:]
    paper.append(s)
    print(paper)
    return paper

pat_time = re.compile(r'[^0-9](19[89][0-9]|20[0-4][0-9]|2050)[^0-9]')
pat = re.compile('[,，.。;；、:：]')
def find_year(text):
    return pat_time.findall(' ' + text + ' ')

def find_longest(li):
    nums = [len(x) for x in li]
    max_num_index_list = map(nums.index, heapq.nlargest(2, nums))
    return [li[x] for x in list(max_num_index_list)]

def isPaper(text):
    pat = re.compile('该文档|本站不保证|万元|基金|项目|专利|ZL[0-9]+|考研网|新闻网|爱学术|简介|https?://|万人计划|奖|创业|专项|主持|参与|攻读|助教|讲师|校长|大夫|教授|主任|学位|学者|负责|课题|目录|院长|所长|书记|工作|简历')
    if len(pat.findall(text)) != 0 or len(find_year(' ' + text + ' ')) >= 3 or len(text) < 30:
        return False
    return True

def crawl(query):
    param = { 'wd' : query , 'pn': str(0)}
    url = 'http://xueshu.baidu.com/s'
    # Add headers
    header = { 'User-Agent':  'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
                'Host': 'xueshu.baidu.com',
                'Referer': 'http://xueshu.baidu.com'
                }
    param = {'wd': query, 'tn': 'SE_baiduxueshu_c1gjeupa', 'ie': 'utf-8', 'sc_hit': '1'}
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    r = requests.get(url=url, params=param, headers=header, allow_redirects=False, verify=False)
    soup = BeautifulSoup(r.content, 'html.parser')
    # print(soup.prettify())
    for item in soup.find_all(name='div', attrs={"class": "result sc_default_result xpath-log"}):
        tit = item.find(name='a', attrs={"data-click": "{'button_tp':'title'}"})
        # print(tit)
        if str(tit).find('<em>') == -1:
            return None
        title = "".join(list(tit.strings))
        author = [i.string for i in item.findAll(name='a', attrs={"data-click": "{'button_tp':'author'}"})]
        if item.find(name='a', attrs={"data-click": "{'button_tp':'sc_cited'}"}):
            count = item.find(name='a', attrs={"data-click": "{'button_tp':'sc_cited'}"}).string.strip()
        else:
            count = None
        label = [i.string for i in item.findAll(name='a', attrs={"data-click": "{'button_tp':'sc_search'}"})]
        if item.find(name='span', attrs={'class': 'sc_time'}):
            year = item.find(name='span', attrs={'class': 'sc_time'}).get('data-year', None)
        else:
            year = None
        if item.find(name='a', attrs={'data-click': "{'button_tp':'publish'}"}):
            source = item.find(name='a', attrs={'data-click': "{'button_tp':'publish'}"}).get('title', None)
        else:
            source = None
        return {'title': title, 'authors': author, 'year': year, 'source': source, 'label': label, 'count': count}

def fetch_pubs_from_webpage(text):
    pubs_new=[]
    s = text.replace('\n', ' ')
    res = {']': [], ')': [], '.': [], '、': [], '）': []}
    for k in res:
        now = 0
        last = 0
        while True:
            mats = '%d\\%s' % (now + 1, k)
            # print(mats)
            mat = re.search(mats, s[last:])
            if mat is None:
                # res[k].append(s[last:].find('\n')) # 丢掉了最后一条
                break
            last += mat.start()
            res[k].append(mat.start())
            now += 1
    # print(tj)
    mac = ''
    ma = 0
    for k in res:
        if len(res[k]) > ma:
            ma = len(res[k])
            mac = k
    if ma == 0:
        pubs_ini= []
    # print(ma, mac)
    if mac=='':
        return
    paper = []
    s = s[res[mac][0]:]
    for i in range(1, len(res[mac])):
        paper.append(s[:res[mac][i]])
        s = s[res[mac][i]:]
    # return paper
    new_paper = []
    now = len(paper)
    for i in range(-1, -len(paper) - 1, -1):
        # print(paper[i])
        while paper[i].rfind('%d%s' % (now, mac)) != -1:
            p = paper[i].rfind('%d%s' % (now, mac))
            # print(p)
            if len(paper[i][p:]) < 30:
                p = paper[i].find('%d%s' % (now, mac))
            new_paper.append(paper[i][p:])
            paper[i] = paper[i][:p]
            now -= 1
            if now == 0:
                break
        if now == 0:
            break
    pubs_ini=list(reversed(new_paper))
    for item in pubs_ini:
        if isPaper(item):
            # print(item)
            pubs_new.append(item)
    res=[]
    for s in pubs_new:
        li = pat.split(s)
        th = crawl(' '.join(find_longest(li)))
        if th is not None:
            res.append(th)
        time.sleep(1)
    return res







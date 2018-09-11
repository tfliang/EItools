import json

import re

import jieba
import tensorflow as tf

from EItools.client.mongo_client import MongoDBClient
from EItools.extract.interface import extract_one_3, print_tag, interface, extract_project


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
pattern_time = r'([1-2][0-9]{3}[年|.|/]?[0-9]{0,2}[月]?)'
pattern_work_time=r'([1-2][0-9]{3}[年./]?[0-9]{0,2}[月]?[-－-]?(?:[1-2][0-9]{3}[年|.|/]?[0-9]{0,2}[月]?|至今)?(?:[^0-9]))'
#国务院学位委员会学科评议组(化学组)成员
def find_soc(text):
    aff_list=find_aff(text)
    # time=re.findall(pattern_time,text)
    # for t in time:
    #     text.replace(t,"")
    if aff_list is not None and len(aff_list)>0:
        for aff in aff_list:
            pattern_title=r''
        aff=' '.join(aff_list)
        most_index=0
        index_value=0
        for i,aff_one in enumerate(aff_list):
            index=text.index(aff_one)
            if index>index_value:
                most_index=i

        title=text[text.index(aff[most_index])+len(aff):]
        if '编委' in aff and aff!="编委":
            aff=aff.replace("编委","")
            title+="编委"
        if aff=='编委':
            return None
        #print("time is:{}".format(time))
        print("aff is:{}".format(aff))
        print("title is:{}".format(title))
        academic_org_exp=None
        if title!="" or aff !="":
            academic_org_exp={"title":title,"org":aff}
        return academic_org_exp


#1985.7 南开大学研究生
def find_work(text):
    print(text)
    aff_list = find_aff(text)

    time = re.findall(pattern_work_time, text)

    if aff_list is not None and len(aff_list) > 0:
        for aff in aff_list:
            pattern_title = r''
        #aff = aff_list[0]
        aff="及".join(aff_list)
        #title = text[text.index(aff) + len(aff):]
        title=re.findall(r"(访问学者|教授|副教授|教师|讲师|博士后)",text)
        print("time is:{}".format(time))
        print("aff is:{}".format(aff))
        print("title is:{}".format(title))
        exp = None
        if len(time) > 2:
            exp = {"start": time[0], "end": time[1], "title": title,"inst": aff}
        elif len(time) == 1:
            exp = {"start": time[0], "title": title,"inst": aff}
        elif len(time) == 0:
            exp = {"title": title,"inst": aff}
        return exp

# with open("../data/social2.json",'r') as file:
#     data=json.load(file)
# for t in data:
#     for text in re.split(r'，|。|、|, |',t):
#         find_soc(text)

#1981年本科毕业于湖南师范大学化学系
def find_edu(text):
    aff_list = find_aff(text)

    time = re.findall(pattern_work_time, text)

    if aff_list is not None and len(aff_list) > 0:
        for aff in aff_list:
            pattern_title = r''
        aff = aff_list[0]
        rest_content = text[text.index(aff) + len(aff):]
        degree=""
        diploma=""
        if '本科' in rest_content or '学士' in rest_content:
            degree='学士'
        if '研究生' in rest_content or '硕士' in rest_content :
            degree='硕士'
        if '博士' in rest_content and '博士后' not in rest_content:
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
        if len(time) > 2:
            edu_exp = {"start":time[0] ,"end":time[1], "diploma": diploma, "degree": degree,"inst":aff}
        elif len(time) == 1:
            edu_exp ={"end":time[0],"diploma": diploma, "degree": degree,"inst":aff}
        elif len(time) == 0:
            edu_exp = {"diploma": diploma, "degree": degree,"inst":aff}
        return edu_exp


def find_patent(text):
    inventor_names=find_aff(text)
    patent_number_pattern=r'[0-9]{8}/.[0-9]'
    patent_number=re.findall(patent_number_pattern,text)
    time = re.findall(pattern_time, text)
    print("time is:{}".format(time))
    print("inventor is:{}".format(inventor_names))
    print("patent_number is:{}".format(patent_number))
    patent=None
    if len(time)>2:
        patent={"issue_date":time[0],"inventor_names":inventor_names,"patent_number":patent_number}
    elif len(time)==0:
        patent = {"inventor_names":inventor_names,"patent_number":patent_number}
    return patent

def find_project(text):
    time=re.findall(pattern_time,text)
    project_number=re.findall(r'[0-9a-z]{8,}',text)
    project_funds=re.findall(r'[\d]+[万元]+',text)
    tf.reset_default_graph()
    result=extract_project(text)
    project_cat,project_name= result if result is not None else (None,None)
    print("number is:{}".format(project_number))
    print("funds is:{}".format(project_funds))
    print("project name is:{}".format(project_name))
    print("project cat is:{}".format(project_cat))
    project=None
    if len(time)>2:
        project={"title":project_name,"cat":project_cat,"fund":project_funds,"start":time[0],"end":time[1]}
    elif len(time)==1:
        project = {"title": project_name, "cat": project_cat, "fund": project_funds, "start": time[0]}
    elif len(time)==0:
        project = {"title": project_name, "cat": project_cat, "fund": project_funds}
    return project

def find_socs(text):
    socs=[]
    print(re.split(r'[。.\n,，；;]', text))
    for t in re.split(r'[。.\n,，；;、]', text):
        if t!="":
            soc=find_soc(t)
            if soc is not None:
                socs.append(soc)
    return socs


def find_works(text):
    works=[]
    print(re.split(r'[。\n；;]', text))
    for t in re.split(r'[。\n；;]', text):
        if t!="":
            work=find_work(t)
            if work is not None:
                works.append(work)
    return works

def find_edus(text):
    edus=[]
    print(re.split(r'[。\n；;]', text))
    for t in re.split(r'[。\n；;]', text):
        if t!="":
            edu=find_edu(t)
            if edu is not None:
                edus.append(edu)
    return edus


def find_patents(text):
    patents=[]
    print(re.split(r'[。.\n,，；;]', text))
    for t in re.split(r'[。.\n,，；;]', text):
        if t!="":
            patent=find_patent(t)
            if patent is not None:
                patents.append(patent)
    return patents


def find_projects(text):
    projects=[]
    print(re.split(r'[。\n；;]', text))
    for t in re.split(r'[。\n；;]', text):
        if t!="":
            project=find_project(t)
            tf.reset_default_graph()
            if project is not None:
                projects.append(project)
    return projects

# with open("../data/work2.json",'r') as file:
#     data=json.load(file)
# for t in data:
#     for text in re.split(r'，|。|、|, |', t):
#         find_work(text)
#find_edu("1984/9~1988/7：华中科技大学自动控制系检测技术及工业自动化仪表专业，工学学士学位")

#find_aff("郭灿城,  罗伟平,  周然飞,  李国友,  龚天保,  空气氧化对二甲苯制备对苯二甲酸的方法及设备，ZL  200810143060.3; WO 2010040251 ")

#print("国家自然科学基金项目（2008,1-2010,12 批准号30771780）：非编码小分子RNA在苯并(a)芘诱导细胞恶变中的作用，33万，负责人".split())

#find_edus("\n中山医科大学博士毕业，师从我国著名泌尿外科专家梅骅教授。2006年2月上海交通大学博士后，2007年美国德克萨斯大学西南医学中心访问学者。")
#find_projects("1. 国家自然科学基金项目 （2013,1-2016,12 批准号21277036）：长链非编码RNA--环境化学致癌新生物标志物及其功能探索，80万，负责人。2. 国家自然科学基金项目 （2012,1-2015,12 批准号81172633）：lincRNA在苯并(a)芘诱发肺癌变中的作用，70万，负责人。3. 高等学校博士学科点专项科研基金博导类课题 （2012,1-2014,12 课题编号20114423110002）：循环miRNA作为环境致癌标志物的实验和人群研究，12万，负责人。4. 国家重点基础研究发展计划（973计划）项目（2012,1-2016,8 项目编号2012CB525004）：环境铅暴露致儿童脑发育损伤的机制研究，项目骨干，负责经费60万。")
#find_edus("2004年-2007年，湖南师范大学生命科学学院和法国Rennes 第二大学，获博士学位")
#find_work("2013/11－至今广东海洋大学水产学院副教授2011/12－2013/10美国俄克拉荷马大学环境基因组研究所访问学者2010/01－2011/12广东海洋大学水产学院副教授2004/10－2009/12广东海洋大学水产学院讲师2001/07－2004/09广东海洋大学水产学院助教1995/08－1998/08安徽省郎溪县郎川酒业有限公司技术员主")
#find_work("曾分别于2001年-2004年，就读于湖南师范大学生命科学学院和法国INRA研究所，获硕士学位")
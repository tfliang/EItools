import json

import re

import jieba
import tensorflow as tf

from EItools.client.mongo_client import MongoDBClient
from EItools.extract.interface import extract_one_3, print_tag, interface, extract_project, extract_patent, \
    extract_award


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
patent_time=r'([1-2][0-9]{3})[年|.|/]?'
pattern_time = r'([1-2][0-9]{3}[年|.|/]?[0-9]{0,2}[月]?|至今)'
pattern_work_time=r'([1-2]{1}[0-9]{3}[年./]?[0-9]{0,2}[月]?\s*(?:-|－|—|-|(?:毕业))*\s*(?:(?:[1-2]{1}[0-9]{3}[年|.|/]?[0-9]{0,2}[月]?)?)|至今)'

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
def find_soc(text):
    aff_list=find_aff(text)
    time=re.findall(pattern_time,text)
    for t in time:
        text.replace(t,"")
    if aff_list is not None and len(aff_list)>0:
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
            academic_org_exp={"title":title,"org":aff,"duration":""}
        return academic_org_exp


#1985.7 南开大学研究生
def find_work(text):
    print(text)
    aff_list = find_aff(text)

    time = re.findall(pattern_time, text)
    # if len(time_all)>0:
    #     time=re.split(r'[年./]',time_all[0])
    # else:
    #     time=[]
    if aff_list is not None and len(aff_list) > 0:
        for aff in aff_list:
            pattern_title = r''
        #aff = aff_list[0]
        aff=",".join(aff_list)
        #title = text[text.index(aff) + len(aff):]
        text=re.sub(pattern_time,'',text)
        position=""
        for aff in aff_list:
            text=text.replace(aff,',')
        position=text
        print("time is:{}".format(time))
        print("aff is:{}".format(aff))
        print("positon is:{}".format(position))
        exp = None
        if len(time) >= 2:
            exp = {"start": time[0], "end": time[1], "position": position,"inst": aff}
        elif len(time) == 1:
            exp = {"start": time[0], "position": position,"inst": aff}
        elif len(time) == 0:
            exp = {"position": position,"inst": aff}
        return exp

# with open("../data/social2.json",'r') as file:
#     data=json.load(file)
# for t in data:
#     for text in re.split(r'，|。|、|, |',t):
#         find_soc(text)

#1981年本科毕业于湖南师范大学化学系
def find_edu(text):
    aff_list = find_aff(text)

    time = re.findall(pattern_time, text)

    if aff_list is not None and len(aff_list) > 0:
        for aff in aff_list:
            pattern_title = r''
        aff = aff_list[0]
        try:
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
            if len(time) >= 2:
                edu_exp = {"start":time[0] ,"end":time[1], "diploma": diploma, "degree": degree,"inst":aff}
            elif len(time) == 1:
                edu_exp ={"end":time[0],"diploma": diploma, "degree": degree,"inst":aff}
            elif len(time) == 0:
                edu_exp = {"diploma": diploma, "degree": degree,"inst":aff}
            return edu_exp
        except Exception as e:
            print(e)
            return None


def find_patent(text):
    inventor_names=find_name(text)
    patent_number_pattern=r'((?:ZL|CN|JP)?[0-9X]{8,15}.{0,1}[0-9X]{0,1})'
    patent_number=re.findall(patent_number_pattern,text)
    text=re.sub(patent_number_pattern,"",text)
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
        patent = {"inventor_names":','.join(inventor_names) if inventor_names is not None else "","patent_number":''.join(patent_number) if patent_number is not None else "" ,"issue_date":time[0] if time is not None and len(time)>0 else "","issue_by":"","title":patent_name}
    elif len(time)==1:
        patent = {"inventor_names":','.join(inventor_names) if inventor_names is not None else "","patent_number":''.join(patent_number) if patent_number is not None else "" ,"issue_date":time[0] if time is not None and len(time)>0 else "","issue_by":"","title":patent_name}
    elif len(time)==0:
        patent = {"inventor_names":','.join(inventor_names) if inventor_names is not None else "","patent_number":''.join(patent_number) if patent_number is not None else "" ,"issue_date":time[0] if time is not None and len(time)>0 else "","issue_by":"","title":patent_name}
    return patent

def find_project(text):
    project_number=re.findall(r'[0-9a-zA-Z]{8,}',text)
    text=re.sub(r'[0-9a-zA-Z]{8,}',"",text)
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
        project={"title":project_name,"cat":project_cat,"fund":project_funds,"start":time[0],"end":time[1],"role":"负责人","code":project_number}
    elif len(time)==1:
        project = {"title": project_name, "cat": project_cat, "fund": project_funds, "start": time[0]}
    elif len(time)==0:
        project = {"title": project_name, "cat": project_cat, "fund": project_funds}
    return project

def find_award(text):
    time=re.findall(pattern_time,text)
    tf.reset_default_graph()
    result = extract_award(text)
    award_title, award_name = result if result is not None else (None, None)
    # title_all=re.findall(r'(国家|省|市|自治区|政府|协会|学会|国务院)[\u4e00-\u9fa5]*?(科学|技术|进步|自然|发明|科技){1,}\s*?奖',text)
    #title=title_all[0] if len(title_all)>0  else ""
    time= time[0] if len(time)>0 else ""
    title=''.join(award_title) if award_title is not None else ""
    name=''.join(award_name) if award_name is not None else ""
    award=None
    if title=="" and name=="":
        return award
    if title!=""  or name !="":
        award={'title':title,'year':time,'award':name}
    return award

def find_socs(text):
    socs=[]
    #datas = re.findall(pattern_work_time, text)
    #socs_all = []
    #if len(datas) > 0:
        #indexs = [m.span()[0] for m in re.finditer(pattern_work_time, text)]
        #socs_all = [text[indexs[i]:indexs[i + 1]] for i, data in enumerate(indexs) if i < len(indexs) - 1]
        #socs_all.append(text[indexs[len(indexs) - 1]:len(text)])
    #if len(socs_all) == 0:
    socs_all = re.split(r'[。.\n,，；;、]', text)
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
        indexs = [text.index(data) for data in datas]
        works_all = [text[indexs[i]:indexs[i + 1]] for i, data in enumerate(indexs) if i < len(indexs) - 1]
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
    sequence_pattern='(\d[．.]\s*[\u4e00-\u9fa5]+)'
    sequence_pattern_second='([(【[（]?\d\s*[)）]】?\s*[\u4e00-\u9fa5])'
    datas = [m.group() for m in re.finditer(sequence_pattern_second, text)]
    indexs = [m.span()[0] for m in re.finditer(sequence_pattern_second,text)]
    if len(datas) == 0:
        datas = [m.group() for m in re.finditer(sequence_pattern, text)]
        indexs = [m.span()[0] for m in re.finditer(sequence_pattern, text)]
    patents_all = []
    if len(datas) > 0:
         patents_all = [text[indexs[i]:indexs[i + 1]] for i, d in enumerate(indexs) if i < len(indexs) - 1]
         patents_all.append(text[indexs[len(indexs) - 1]:len(text)])
    if len(patents_all) == 0:
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
    sequence_pattern = '(\d[．.]+\s*[\u4e00-\u9fa5]+)'
    sequence_pattern_second = '([【[（\[]?\d\s*[\]）]】?\s*[\u4e00-\u9fa5])'
    '[\d\s*]?\s*'
    datas = [m.group() for m in re.finditer(sequence_pattern_second, text)]
    indexs = [m.span()[0] for m in re.finditer(sequence_pattern_second, text)]
    if len(datas) == 0:
        datas = [m.group() for m in re.finditer(sequence_pattern, text)]
        indexs = [m.span()[0] for m in re.finditer(sequence_pattern, text)]
    projects_all = []
    if len(datas) > 0:
        projects_all = [text[indexs[i]:indexs[i + 1]] for i, data in enumerate(indexs) if i < len(indexs) - 1]
        projects_all.append(text[indexs[len(indexs) - 1]:len(text)])
    if len(projects_all) == 0:
        if '。' in text:
            projects_all = re.split(r'[。\n；;]', text)
        else:
            projects_all = re.split(r'[。\n；;,，]', text)
    print(projects_all)
    for t in projects_all:
        if t!="":
            project=find_project(t)
            tf.reset_default_graph()
            if project is not None:
                projects.append(project)
    return projects

def find_awards(text):
    awards=[]
    datas = re.findall(r'([(【[（]?\d\s*[)）]】?\s*[\u4e00-\u9fa5]?)', text)
    if len(datas)==0:
        datas = re.findall(r'(\d[．.][\u4e00-\u9fa5^]?)', text)
    awards_all=[]
    if len(datas)>0:
        indexs=[text.index(data) for data in datas]
        awards_all=[text[indexs[i]:indexs[i+1]] for i,data in enumerate(indexs) if i<len(indexs)-1]
        awards_all.append(text[indexs[len(indexs)-1]:len(text)])
    if len(awards_all)==0:
        awards_all=re.split(r'[。\n；;]', text)
    print(awards_all)
    for t in awards_all:
        if t!="":
            award=find_award(t)
            tf.reset_default_graph()
            if award is not None:
                awards.append(award)
    return awards

def find_awards_list(awd_list):
    awd_aparts=[]
    if awd_list is not None:
        for awd in awd_list:
            awd_apart=find_awards(awd)
            for a in awd_apart:
                awd_aparts.append(a)
    return awd_aparts
#print("美国肯塔基大学制造研究中心 访问教授 ".replace("美国肯塔基大学制造研究中心",","))

#print(find_project("3.国家基础研究计划（973）（2012CB910800）：炎症诱导肿瘤的分子调控网络研究, 240万元课题负责人2012.1-2016.12"))

#print(find_work("1998年至今任国家重大科学工程“兰州重离子加速器冷却储存环HIRFL-CSR”的总工程师兼CSR总体室主任"))
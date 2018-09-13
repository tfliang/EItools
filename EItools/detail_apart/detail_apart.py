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
pattern_time = r'([1-2][0-9]{3}[年|.|/-]?[0-9]{0,2}[月]?)'
pattern_work_time=r'([1-2][0-9]{3}[年./]?[0-9]{0,2}[月]?\s*(?:-|－|-|(?:毕业))*\s*(?:[1-2][0-9]{3}[年|.|/]?[0-9]{0,2}[月]?|至今)?)[^0-9]'

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

    time = re.findall(pattern_time, text)

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
    inventor_names=find_name(text)
    patent_number_pattern=r'((ZL|CN|JP)?[0-9X]{9,15}.{0,1}[0-9X]{0,1})'
    patent_number=re.findall(patent_number_pattern,text)
    tf.reset_default_graph()
    patent_name=extract_patent(text)
    time = re.findall(pattern_time, text)
    print("time is:{}".format(time))
    print("inventor is:{}".format(inventor_names))
    print("patent_number is:{}".format(patent_number))
    patent=None
    if len(time)>2:
        patent = {"inventor_names":','.join(inventor_names) if inventor_names is not None else "","patent_number":''.join(patent_number) if patent_number is not None else "" ,"issue_date":"","issue_by":"中华人民共和国国家知识产权局","title":patent_name}
    elif len(time)==0:
        patent = {"inventor_names":','.join(inventor_names) if inventor_names is not None else "","patent_number":''.join(patent_number) if patent_number is not None else "" ,"issue_date":"","issue_by":"中华人民共和国国家知识产权局","title":patent_name}
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
    print("project time is:{}".format(time))
    project_name=''.join(project_name) if len(project_name) is not None else""
    project_cat=''.join(project_cat) if len(project_cat) is not None else ""
    project_funds=''.join(project_funds) if len(project_funds) is not None else ""
    project=None
    if len(time)>2:
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
    title=award_title if award_title is not None else ""
    name=award_name if award_name is not None else ""
    award=None
    if title!="" or time!="" or name !="":
        award={'title':title,'year':time,'award':name}
    return award

def find_socs(text):
    socs=[]
    datas = re.findall(pattern_work_time, text)
    socs_all = []
    if len(datas) > 0:
        indexs = [text.index(data) for data in datas]
        socs_all = [text[indexs[i]:indexs[i + 1]] for i, data in enumerate(indexs) if i < len(indexs) - 1]
        socs_all.append(text[indexs[len(indexs) - 1]:len(text)])
    if len(socs_all) == 0:
        socs_all = re.split(r'[。.\n,，；;、]', text)
    for t in socs:
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
    for t in works_all:
        if t!="":
            work=find_work(t)
            if work is not None:
                works.append(work)
    return works

def find_edus(text):
    edus=[]
    datas = re.findall(pattern_work_time, text)
    edus_all = []
    if len(datas) > 0:
        indexs = [text.index(data) for data in datas]
        edus_all = [text[indexs[i]:indexs[i + 1]] for i, data in enumerate(indexs) if i < len(indexs) - 1]
        edus_all.append(text[indexs[len(indexs) - 1]:len(text)])
    if len(edus_all) == 0:
        edus_all = re.split(r'[。\n；;]', text)
    for t in edus_all:
        if t!="":
            edu=find_edu(t)
            if edu is not None:
                edus.append(edu)
    return edus


def find_patents(text):
    patents=[]
    datas = re.findall(r'(\d[．.][\u4e00-\u9fa5]?)', text)
    if len(datas) == 0:
        datas = re.findall(r'([(【[（]?\d\s*[)）]】?\s*[\u4e00-\u9fa5]?)', text)
    patents_all = []
    if len(datas) > 0:
        indexs = [text.index(data) for data in datas]
        patents_all = [text[indexs[i]:indexs[i + 1]] for i, data in enumerate(indexs) if i < len(indexs) - 1]
        patents_all.append(text[indexs[len(indexs) - 1]:len(text)])
    if len(patents_all) == 0:
        patents_all = re.split(r'[。\n；;]', text)
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
    datas = re.findall(r'(\d[．.][\u4e00-\u9fa5]?)', text)
    if len(datas) == 0:
        datas = re.findall(r'([(【[（]?\d\s*[)）]】?\s*[\u4e00-\u9fa5]?)', text)
    projects_all = []
    if len(datas) > 0:
        indexs = [text.index(data) for data in datas]
        projects_all = [text[indexs[i]:indexs[i + 1]] for i, data in enumerate(indexs) if i < len(indexs) - 1]
        projects_all.append(text[indexs[len(indexs) - 1]:len(text)])
    if len(projects_all) == 0:
        projects_all = re.split(r'[。\n；;]', text)
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
    datas=re.findall(r'(\d[．.][\u4e00-\u9fa5]?)',text)
    if len(datas)==0:
        datas=re.findall(r'([(【[（]?\d\s*[)）]】?\s*[\u4e00-\u9fa5]?)', text)
    awards_all=[]
    if len(datas)>0:
        indexs=[text.index(data) for data in datas]
        awards_all=[text[indexs[i]:indexs[i+1]] for i,data in enumerate(indexs) if i<len(indexs)-1]
        awards_all.append(text[indexs[len(indexs)-1]:len(text)])
    if len(awards_all)==0:
        awards_all=re.split(r'[。\n；;，,]', text)
    print(awards_all)
    for t in awards_all:
        print(t)
        if t!="":
            award=find_award(t)
            tf.reset_default_graph()
            if award is not None:
                awards.append(award)
    return awards

#print(find_awards("[1] “浙江省舟山市沈家门小学”, 专业负责人， 获2003年度建设部优秀勘察设计二等奖；[2]"))
#find_project("郭灿城,  王旭涛,  刘强,  选择性催化空气氧化甲苯和取代甲苯成醛和醇的方法, ZL 03118066.3 ")
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
#find_work("1986年毕业至今，工作于广州中医药大学")
#find_award("2005年山东省科技进步一等奖，第一完成人")

#find_awards("1．土壤重金属污染发生机理与修复原理，辽宁省自然科学一等奖（2008），排名：周启星、马奇英、孙铁珩、贾永锋、魏树和、王美娥、郭观林等，中国科学院沈阳应用生态研究所等，2006-12-062．污染土壤的植物修复技术与应用，辽宁省科技进步二等奖（2006），排名：周启星、魏树和、陈晓东、常文越、李法云、王晓飞、李培军、曹伟、王美娥、宋玉芳、王新、任丽萍、张倩茹等，中国科学院沈阳应用生态研究所等，2005-12-053．生态安全复合高效絮凝剂研制及在水处理中的应用，辽宁省科技进步二等奖（2005），排名：周启星、张凯松、张倩茹、刘睿、王新、魏树和、籍国东、任丽萍、刘宛、孙铁珩等")

#find_works("大学高分子系，博士(导师：沈之荃院士) 1993.09 - 1996.06 杭州大学化学系，硕士(导师：龚钰秋教授) 1989.09 - 1993.06 杭州师范学院化学系本科")
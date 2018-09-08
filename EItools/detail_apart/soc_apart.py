import json

import re
from nn import tf

from EItools.client.mongo_client import MongoDBClient
from EItools.extract.interface import extract_one_3,print_tag


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
pattern_time = r'([1-2][0-9]{3}[年|.|/]?[0-9]{0,2}[月]?)'

#国务院学位委员会学科评议组(化学组)成员
def find_soc(text):
    aff_list=find_aff(text)
    time=re.findall(pattern_time,text)

    if aff_list is not None and len(aff_list)>0:
        for aff in aff_list:
            pattern_title=r''
        aff=aff_list[0]
        title=text[text.index(aff)+len(aff):]
        print("time is:{}".format(time))
        print("aff is:{}".format(aff))
        print("title is:{}".format(title))

#1985.7 南开大学研究生
def find_work(text):
    aff_list = find_aff(text)

    time = re.findall(pattern_time, text)

    if aff_list is not None and len(aff_list) > 0:
        for aff in aff_list:
            pattern_title = r''
        aff = aff_list[0]
        title = text[text.index(aff) + len(aff):]
        print("time is:{}".format(time))
        print("aff is:{}".format(aff))
        print("title is:{}".format(title))

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
        if '本科' in rest_content:
            degree='本科'
        if '研究生' in rest_content:
            degree='硕士'
        if '博士' in rest_content:
            degree='博士'
        if '学士' in rest_content or '本科' in rest_content:
            diploma='本科'
        if '研究生' in rest_content or '硕士' in rest_content or '博士' in rest_content:
            diploma='研究生'
        print("time is:{}".format(time))
        print("aff is:{}".format(aff))
        print("degree is:{}".format(degree))

def find_patent(text):
    inventor_names=find_aff(text)
    patent_number=r'[0-9]{8}/.[0-9]'
    time = re.findall(pattern_time, text)
    print("time is:{}".format(time))
    print("inventor is:{}".format(inventor_names))
    print("patent_number is:{}".format(patent_number))

def find_project(text):
    time=re.findall(pattern_time,text)
    project_number=re.findall(r'[0-9a-z]{8,}',text)
    project_funds=re.findall(r'[\d]+[万元]+',text)
    project_name=""
    print("number is:{}".format(project_number))
    print("funds is:{}".format(project_funds))
    print("project name is:{}".format(project_name))


# with open("../data/work2.json",'r') as file:
#     data=json.load(file)
# for t in data:
#     for text in re.split(r'，|。|、|, |', t):
#         find_work(text)
#find_edu("1984/9~1988/7：华中科技大学自动控制系检测技术及工业自动化仪表专业，工学学士学位")

#find_aff("郭灿城,  罗伟平,  周然飞,  李国友,  龚天保,  空气氧化对二甲苯制备对苯二甲酸的方法及设备，ZL  200810143060.3; WO 2010040251 ")

print("国家自然科学基金项目（2008,1-2010,12 批准号30771780）：非编码小分子RNA在苯并(a)芘诱导细胞恶变中的作用，33万，负责人".split())




import datetime
import json

import re

from bson import ObjectId
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from EItools.client.mongo_client import MongoDBClient
from EItools.crawler.crawl_information import start_crawl, crawl_person_info
from EItools.crawler.task import task_status_dict

from EItools.extract.interface import interface
from EItools.detail_apart import detail_apart
mongo_client=MongoDBClient()
persons=mongo_client.get_crawled_person(0,100)
def clean_word(text):
    text = text.replace('\xa0', '').replace('\u3000', '').strip()#.replace('\n', '')
    return text

def clean_list(lst):
    new_lst = []
    for item in lst:
        new_lst.append(clean_word(item))
    return list(set(new_lst))

def print_tag(lst, name, text):
    temp = clean_list(lst)
    text = clean_word(text)
    cnt = [text.count(word) for word in temp]
    string=name+': '
    for i, v in enumerate(temp):
        str1=str(temp[i]) + '(' + str(cnt[i]) + '),'
        string +=str1
        string +='\n'
    return string

def delete_tag():
    with open('test_data_standard.txt','r') as f:
        data=f.read()
        data = data.split("*********&&&&&&&&")
        with open('test_data_standard2.txt', 'w+') as w:
            for d in data:
                text=re.sub('<[//a-zA-Z]+?>',"",d)
                w.write(text)
                w.write("\n")
                w.write("*********&&&&&&&&")


#delete_tag()
def gen_data():
    with open('extract_result_standard_new_detail.txt','w+') as w:
        #for id in persons:
        with open('test_data_standard2.txt','r') as f:
            data=f.read()
            infos=data.split("*********&&&&&&&&")
            #p=mongo_client.get_crawled_person_by_pid(id)
            for info in infos:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                #if 'info' in p and p['info'] !="":
                if info!="":
                    #text=p['info']
                    text=info
                    #w.write(id)
                    w.write('\r\n')
                    PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ=interface(info)
                    # w.write('PER:'+''.join(PER))
                    # w.write('\r\n')
                    # w.write('ADR:'+''.join(ADR))
                    # w.write('\r\n')
                    # w.write('AFF:'+''.join(AFF))
                    # w.write('\r\n')
                    # w.write('TITLE:'+''.join(TIT))
                    # w.write('\r\n')
                    # w.write('JOB:'+''.join(JOB))
                    # w.write('\r\n')
                    # w.write('DOM:'+''.join(DOM))
                    # w.write('\r\n')
                    # w.write('EDU:'+''.join(EDU))
                    # w.write('\r\n')
                    # w.write('WRK:'+''.join(WRK))
                    # w.write('\r\n')
                    # w.write('SOC'+''.join(SOC))
                    # w.write('\r\n')
                    # w.write('AWD'+''.join(AWD))
                    # w.write('\r\n')
                    # w.write('PAT'+''.join(PAT))
                    # w.write('\r\n')
                    # w.write('PRJ'+''.join(PRJ))
                    # w.write('\r\n')
                    str_list=[]
                    if PER is not None:
                        str1=print_tag(PER, 'PER', text)
                        #str1='/n'.join(PER)
                        str_list.append(str1)
                    if ADR is not None:
                        str1=print_tag(ADR, 'ADR', text)
                        #str1='/n'.join(ADR)
                        str_list.append(str1)
                    if AFF is not None:
                        str1=print_tag(AFF, 'AFF', text)
                        #str1='/n'.join(AFF)
                        str_list.append(str1)
                    if TIT is not None:
                        str1=print_tag(TIT, 'TIT', text)
                        #str1='/n'.join(TIT)
                        str_list.append(str1)
                    if JOB is not None:
                        str1=print_tag(JOB, 'JOB', text)
                        #str1='/n'.join(JOB)
                        str_list.append(str1)
                    if DOM is not None:
                        str1=print_tag(DOM, 'DOM', text)
                        #str1='/n'.join(DOM)
                        str_list.append(str1)
                    if EDU is not None:
                        str1=print_tag(EDU, 'EDU', text)
                        #str1='/n'.join(EDU)
                        str_list.append(str1)
                    if WRK is not None:
                        str1=print_tag(WRK, 'WRK', text)
                        #str1='/n'.join(WRK)
                        str_list.append(str1)
                    if SOC is not None:
                        #str1='/n'.join(SOC)
                        str1=print_tag(SOC, 'SOC', text)
                        str_list.append(str1)
                    if AWD is not None:
                        #str1='/n'.join('AWD')
                        str1=print_tag(AWD, 'AWD', text)
                        str_list.append(str1)
                    if PAT is not None:
                        #str1='/n'.join('PAT')
                        str1=print_tag(PAT, 'PAT', text)
                        str_list.append(str1)
                    if PRJ is not None:
                        #str1='/n'.join(PRJ)
                        str1=print_tag(PRJ, 'PRJ', text)
                        str_list.append(str1)
                    w.write('\n'.join(str_list))
                    w.write('\n')
                    w.write('######')
                    #PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ
                    EDU=detail_apart.find_edus('/n'.join(EDU))
                    WRK= detail_apart.find_works('/n'.join(WRK))
                    SOC = detail_apart.find_socs('/n'.join(SOC))
                    AWD = detail_apart.find_awards('/n'.join(AWD))
                    PAT = detail_apart.find_patents('/n'.join(PAT))
                    PRJ = detail_apart.find_projects('/n'.join(PRJ))
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
def make_data():
    mongo_client=MongoDBClient()
    p=mongo_client.get_crawled_person_by_pid("5b8673bb8d431519256c32c6")
    if p is not None:
        p['edu_detail'] = detail_apart.find_edus(p['edu'])
        p['exp_detail'] = detail_apart.find_works(p['exp'])
        p['academic_org_exp_detail'] = detail_apart.find_socs(p['academic_org_exp'])
        #p['awards']=soc_apart.find(p['awards'])
        p['patents_detail'] = detail_apart.find_patents(p['patents'])
        p['projects_detail'] = detail_apart.find_projects(p['projects'])
        p['awards_detail']=detail_apart.find_awards(p['awards'])
        mongo_client.save_crawled_person(p)

#make_data()
#gen_data()


persons = mongo_client.get_uncrawled_person_by_taskId("5b9a33608d431508dea40b74")
if len(persons) > 0:
    print(len(persons))
    # try:
    #persons=persons[25:500]
    crawl_person_info(persons, "5b9a33608d431508dea40b74")
    mongo_client.update_task(task_status_dict['finished'], "5b9a33608d431508dea40b74")

#mongo_client.db['uncrawled_person'].update({'task_id':ObjectId('5b9a33608d431508dea40b74')},{"$set":{"status":1}})
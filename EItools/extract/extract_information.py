import json

import re

from bson import ObjectId

from EItools.client.mongo_client import MongoDBClient
from EItools.config import globalvar
from EItools.extract.interface import interface
from EItools.chrome.crawler import InfoCrawler

with open(globalvar.FILE_CONFIG) as f:
    config_crawlers=json.load(f)
with open(globalvar.DATA_DICT) as f:
    data_dict=json.load(f)
# with open(globalvar.DATA_DICT,"w") as f:
#     regex_dict=data_dict["regex_dict"]
#     t=dict()
#     for key,value in regex_dict.items():
#         for v in re.split('\\|',value):
#             t[v]=key
#     data_dict['dict']=t
#     f.write(str(data_dict))
def extract(content,p):
    info=dict()
    regex = ""
    regex_dict = data_dict["regex_dict"]
    for key, value in regex_dict.items():
        regex += value
    all_match = re.finditer(regex, content)
    l_m = list(enumerate(all_match))
    if all_match is not None and len(l_m) > 0:
        s_pre = l_m[0][1].start()
        e_pre = l_m[0][1].end()
        for i, m in l_m:
            if i > 0:
                s = m.start()
                e = m.end()
                c = content[s_pre:s]
                if m.group() not in info:
                    info[m.group()] = ""
                info[m.group()] += c
                s_pre = s
                e_pre = e
                if i == (len(l_m) - 1):
                    c = content[s:]
                    if m.group() not in info:
                        info[m.group()] += c
    info2 = dict()
    for key, value in info.items():
        if data_dict['dict'][key] not in info:
            info2[data_dict['dict'][key]] = ""
        info2[data_dict['dict'][key]] += info[key]
    bs_part = re.split('[，|;|；|。|,|<k> ]', info2['basic_info'] + info2['exprience'])
    p['title'] = []
    p['position'] = []
    for s in bs_part:
        for t in data_dict['title']:
            if t in s:
                p['title'].append(s)
        for t in data_dict['position']:
            if t in s:
                p['position'].append(s)
    for s in bs_part:
        for t in data_dict['degree']:
            if t in s:
                p['degree'] = t
                p['diploma'] = data_dict['diploma'][t]
                break
    return p

mongo_client=MongoDBClient()
def extract_info_from_db(id):
    persons=mongo_client.get_crawled_person_by_taskId(id)
    print(len(persons))
    part_list=[]
    for i,person in enumerate(persons):
        p=person
        del p["_id"]
        del p['taskId']
        if 'info' in person and person['info']!="":
            result = interface(person['info'])
            PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ = result if result is not None else (
            None, None, None, None, None, None, None, None, None, None, None, None)
            p['PER']=PER
            p['ADR']=ADR
            p['AFF']=AFF
            p['TIT']=TIT
            p['JOB']=JOB
            p['DOM']=DOM
            p['EDU']=EDU
            p['WRK']=WRK
            p['SOC']=SOC
            p['AWD']=AWD
            p['PAT']=PAT
            p['PRJ']=PRJ
            # p['aff'] = AFF
            # p['title'] = TIT
            # p['job'] = JOB
            # p['achieve'] = DOM
            # p['awards'] = AWD
            # p['exp'] = WRK
            # p['patents'] = PAT
            # p['projects'] = PRJ
            # p['academic_org_exp'] = SOC

            part_list.append(p)
            if i%2==0:
                print(i)
                with open('data1.json','r') as fw:
                    person_list=json.load(fw)
                person_list=person_list+part_list
                with open('data1.json', 'w') as fw:
                    json.dump(person_list,fw,ensure_ascii=False)

#extract_info_from_db("5b1d547d0fa2b8a4bb786d51")
def extract_info():
    with open('data2.json','r') as fw:
        line=fw.readline()
        print(len(re.findall(r'\{(.*?)\}\{"name"',line)))
        i=0
        for data in re.finditer(r'\{(.*?)\}\{"name"',line):
            i=i+1
            print(i)
            l=len(data.group())
            print(data.group()[0:l-7])
            result = json.loads(data.group()[0:l-7])
#extract_info()

def split_json():
    with open('data1.json','r') as fw:
        data=json.load(fw)
        with open('data_experts.json','w') as f:
            json.dump(data[5:105],f,ensure_ascii=False)
#split_json()

def test_crawl():
    persons = [{'name': 'GEOFFREYMICHAELGADD', 'org': '中国科学院新疆生态与地理研究所','_id':"5b5f02a4421aa9031208072d"}]
    if len(persons) > 0:
        infoCrawler = InfoCrawler()
        infoCrawler.load_crawlers()
        for i, p in enumerate(persons):
            person = {}
            print(p['name'])
            person['name'] = p['name']
            #affs = pre_process.get_valid_aff(p['org'])
            person['simple_affiliation'] = p['org']
            #success,p1=get_data_from_aminer(person)
            success=False
            if success:
                #p = p1
                p['source'] = 'aminer'
                mongo_client.save_crawled_person(p)
            else:
                info, url = infoCrawler.get_info(person)
                emails_prob = infoCrawler.get_emails(person)
                citation, h_index = infoCrawler.get_scholar_info(person)
                # if affs is not None:
                #     p['s_aff'] = affs
                p['url'] = url
                p['info'] = info
                p['citation'] = citation
                p['h_index'] = h_index
                # p = extract_information.extract(info, p)
                #result = interface(info)
                #PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ = result if result is not None else (
                #None, None, None, None, None, None, None, None, None, None, None, None)
                # p['aff']=AFF
                # p['title']=TIT
                # p['job']=JOB
                # p['achieve']=DOM
                # p['awards']=AWD
                # p['exp']=WRK
                # p['patents']=PAT
                # p['projects']=PRJ
                # p['academic_org_exp']=SOC

                #
                # p['PER'] = PER
                # p['ADR'] = ADR
                # p['AFF'] = AFF
                # p['TIT'] = TIT
                # p['JOB'] = JOB
                # p['DOM'] = DOM
                # p['EDU'] = EDU
                # p['WRK'] = WRK
                # p['SOC'] = SOC
                # p['AWD'] = AWD
                # p['PAT'] = PAT
                # p['PRJ'] = PRJ
                p['source'] = 'crawler'
                p['emails_prob'] = emails_prob
                mongo_client.save_crawled_person(p)
                # 存入智库

            # mongo_client.rm_person_by_id(p['_id'])
            mongo_client.update_person_by_id(p['_id'])
        infoCrawler.shutdown_crawlers()
#test_crawl()
#mongo_client.update_person_by_id("5b5f02a6421aa90312080770")

def extract_person(small,big):
    #persons = mongo_client.db['crawled_person_final'].find().skip(small).limit(big)
    persons=mongo_client.db['crawled_person_final'].find({"_id":ObjectId('5b642f23a4af2607336f7e2c')})
    for i,p in enumerate(persons):
        if i>=0 and i<big:
            print(i)
            if  'info' in p and p['info'] != "":
                result = interface(p['info'])
                PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ = result if result is not None else (
                None, None, None, None, None, None, None, None, None, None, None, None)
                # p['aff']=AFF
                # p['title']=TIT
                # p['job']=JOB
                # p['achieve']=DOM
                # p['awards']=AWD
                # p['exp']=WRK
                # p['patents']=PAT
                # p['projects']=PRJ
                # p['academic_org_exp']=SOC


                p['PER'] = PER
                p['ADR'] = ADR
                p['AFF'] = AFF
                p['TIT'] = TIT
                p['JOB'] = JOB
                p['DOM'] = DOM
                p['EDU'] = EDU
                p['WRK'] = WRK
                p['SOC'] = SOC
                p['AWD'] = AWD
                p['PAT'] = PAT
                p['PRJ'] = PRJ
                mongo_client.db['crawled_person_final'].save(p)
                mongo_client.db['crawled_person_final'].update({"_id": p['_id']}, {"$set": {"status": 0}})
#while True:
total=20000
offset=16099
size=3000
p_list=[]
extract_person(0,2000)
# while(offset<total):
#     p=Process(target=extract_person,args=(offset,size))
#     p.start()
#     p_list.append(p)
#     offset+=size
# for p_l in p_list:
#     p_l.join()
#     #time.sleep(3000)

def update_status():
    persons=mongo_client.crawed_person_col.find()
    for i, p in enumerate(persons):
        print(i)
        p=mongo_client.get_crawled_person_by_pid(str(p['_id']))
        if 'PER' in p or 'ADR' in p or  'AFF' in p or 'TIT' in p or 'JOB' in p or 'DOM' in p or 'EDU' in p or 'WRK' in p or 'SOC' in p or 'AWD' in p or 'PAT' in p or 'PRJ' in p:
            mongo_client.update_crawled_person_status(str(p['_id']))
#update_status()
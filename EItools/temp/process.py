import csv
import heapq
import json
import string
import sys
import os

from EItools.classifier_mainpage.Extract import Extract

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import re

import cchardet
import requests
from MagicBaidu import MagicBaidu
from MagicGoogle import MagicGoogle
from bson import ObjectId

from EItools.client.mongo_client import mongo_client
from EItools.crawler import crawl_mainpage, crawl_service
from EItools.crawler.crawl_service import select, apart_text, crawl_person_info
from EItools.detail_apart import detail_apart
from EItools.utils.chinese_helper import strQ2B

def process_data():
    collection_person=mongo_client.db['crawled_person_final'].find()
    for i,p in enumerate(collection_person):
        print(i)
        if 'is_new_aff' in p and p['is_new_aff']==1:
            aff=p['ini'].split(',')[1]
            record=True
            for c_aff in p['current-aff']:
                if c_aff.find(aff) !=-1 or aff.find(c_aff) !=-1:
                    record=False
                    break
            mongo_client.db['crawled_person_final'].update({'_id':p['_id']},{'$set':{'change':record}})

#process_data()
def write_csv():
    collection_person = mongo_client.db['crawled_person_final'].find({'change':True})
    csvFile2 = open('csvFile2.csv', 'w', newline='',encoding='utf-8')  # 设置newline，否则两行之间会空一行
    writer = csv.writer(csvFile2)
    for p in collection_person:
        #data = []
        item={}
        item['_id']=str(p['_id'])
        item['current-aff']=','.join(p['current-aff'])
        item['url']=p['url']
        item['ini']=p['ini']
        #data.append(p['_id'])
        #data.append(','.join(p['current-aff']))
        #data.append(p['url'])
        #data.append(p['ini'])
        writer.writerow(item.values())
    csvFile2.close()
#write_csv()

def generate_train_data():
    with open('train_data','w') as w:
        i = 2000
        while i<2800:
            file='/Users/bcj/Documents/科技部/xiaoyan标注完成名单/抽取准确文本（820人）/infoExample{}-{}.txt'.format(i,i+100)
            with open(file,'r') as f:
                content=f.read()
                lines=content.split("*********&&&&&&&&")
                for line in lines:
                    line=line.split('\n')
                    content=' '.join(line[4:])
                    pattern=r'<[^>]+/?>[^>]+(/S)*>'
                    p_list=re.findall(pattern,content)
                    if p_list is not None and len(p_list)>0:
                        for p in p_list:
                            print(p)
                    #w.write(f)
            i=i+100

#generate_train_data()
def panduan(s1,s2):
    j=True
    for s in s1:
        if s not in s2:
            j=False
    return j


def read_data():
    with open('data.csv','w') as w:
        writer=csv.writer(w)
        with open('/Users/bcj/Desktop/待确认名单(部分).csv','r') as f:
            csv_file=csv.reader(f)
            for row,data in enumerate(csv_file):
                if row>0:
                    old=data[3].split(',')[1]
                    new=data[6]
                    if panduan(old,new) or panduan(new,old):
                        continue
                    else:
                       writer.writerow(data)

#read_data()


def transform_data():
    files=['待确认名单ai.csv']
    with open('/Users/bcj/Desktop/要发文件夹/待确认名单.csv','w+') as w:
        writer=csv.writer(w)
        for file in files:
            with open('/Users/bcj/Desktop/要发文件夹/'+file) as f:
                reader=csv.reader(f)
                for i,r in enumerate(reader):
                    id=r[0]
                    person=mongo_client.db['crawled_person_final'].find_one({'_id':ObjectId(id)})
                    if person is not None and 'pos' in person:
                        print(i)
                        r.append(person['pos'])
                    print(r)
                    writer.writerow(r)
#transform_data()

def caculate_change():
    count=0
    with open('/Users/bcj/Desktop/要发文件夹/待确认名单(部分).csv','r') as f:
        data1=list(csv.reader(f))
    with open('/Users/bcj/Desktop/要发文件夹/data对比.csv','r') as f2:
        data2=csv.reader(f2)
        for j,d2 in enumerate(data2):
            for i, d1 in enumerate(data1):
                if d2[1]==d1[3]:
                    #if panduan(d2[2],d1[1]) or panduan(d1[1],d2[2]):
                    if d2[2]==d1[1]:
                        print('{}------{}'.format(d2[2],d1[1]))
                        count=count+1
    print(count)

#caculate_change()

def caculate_rest():
    with open('/Users/bcj/Desktop/要发文件夹/待确认名单.csv','w') as f1:
        writer=csv.writer(f1)
        with open('/Users/bcj/Desktop/要发文件夹/002-待确认名单1.csv','r') as f:
            reader=csv.reader(f)
            for r,data in enumerate(reader):
                with open('/Users/bcj/Desktop/要发文件夹/待确认名单(部分).csv','r') as w:
                    reader_has=list(csv.reader(w))
                flag=True
                for data_has in reader_has:
                    if data[0]==data_has[0]:
                        flag=False
                if flag:
                    try:
                        old = data[3].split(',')[1]
                        new = data[6]
                        if panduan(old, new) or panduan(new, old):
                            continue
                        else:
                            writer.writerow(data)
                    except Exception as e:
                        print(e)

#caculate_rest()
PROXIES = [{
    'http': 'http://159.203.174.2:3128'
}]

mg = MagicGoogle(PROXIES)
mb = MagicBaidu()


def get_res(query):
    res = []
    try:
        for i in mb.search(query=query, pause=0.5):
            if 'domain' in i and('baike.com' in i['domain'] or 'baidu.com' in i['domain']):
                continue
            if 'domain' in i and'官网' in i['title'] :
                print(i)
                if 'domain' in i:
                    #result=re.split('-',i['domain'])
                    return i['domain']
    except Exception as e:
        return ""

def get_domain():
    institutions=mongo_client.db['aff'].find()
    for inst in institutions:
        if inst['domain'] is None or 'baidu.com' in inst['domain'] or 'baike.com' in inst['domain']:
            name=inst['name']
            print(name)
            result=get_res(name)
            print(result)
            inst['domain']=result
            mongo_client.db['aff'].save(inst)

#get_domain()
def save_name():
    with open('/Users/bcj/Desktop/高校中英名单.csv','r') as f:
        reader=csv.reader(f)
        for i,data in enumerate(reader):
            if i>0:
                name=data[0]
                name_en=data[1]
                dict={}
                result = get_res(name)
                dict['name']=name
                dict['name_en']=name_en
                dict['domain']=result
                mongo_client.db['institution'].save(dict)

def save_inst():
    with open('/Users/bcj/Documents/科技部/抽取文档/xingming.csv','r') as w:
        reader=csv.reader(w)
        for i,data in enumerate(reader):
            dict={}
            dict['name']=data[0]
            dict['rare']=data[1]
            dict['total']=data[2]
            mongo_client.db['name_rare'].save(dict)

#save_inst()
#get_domain()
#print(get_res("中国航空工业集团公司"))

def match_data():
    train_data = ['info500-750.txt', '750-1000.txt', 'info1000-1250.txt', '1250-1500.txt', 'infoExample2000-2100.txt',
               'infoExample2100-2200.txt', 'infoExample2200-2300.txt', 'infoExample2400-2500.txt',
               'infoExample2600-2700.txt']
    with open('/Users/bcj/Documents/科技部/patent.txt', 'w+') as w:
        for data in train_data:
            with open("../data/"+data,'r') as f:
                data=f.read()
                text=re.findall('<patent>.*?</patent>',data)
                print(len(text))
                w.write('\r\n*******\r\n'.join(text))

#match_data()

def write_data():
    with open('/Users/bcj/Documents/科技部/award.json','r') as f:
        data=json.load(f)
        for d in data:
            s=d[7:len(d)-7]
            print(s)

#write_data()

def test_data():
    persons = mongo_client.get_crawled_person_by_taskId("5b8673ba8d431519256c32c5")
    for person in persons:
        person['_id']=ObjectId(person['id'])
        persons_info = crawl_person_info([person], None)


#test_data()

def export_data():
    #person_ids=["5b9a33778d431508dea40be2","5b9a33768d431508dea40be0","5b9a33768d431508dea40bdf","5b9a33788d431508dea40be6","5b9a33788d431508dea40be7","5b9a33788d431508dea40be8"]
    person_ids = ["5b9a33778d431508dea40be2", "5b9a33768d431508dea40be0", "5b9a33768d431508dea40bdf",
                  "5b9a33788d431508dea40be6", "5b9a33788d431508dea40be7", "5b9a33788d431508dea40be8",
                  "5b9a341e8d431508dea40ee0", "5b9abce9c3666e23ba80d3da"]
    persons=[]
    for id in person_ids:
        person=mongo_client.db['crawled_person_final'].find_one({"_id":ObjectId(id)},{'name':1,'aff':1,'position':1,'domain':1,'honors':1,'gender':1,'title':1
            ,'edu_exp':1,'exp':1,'academic_org_exp':1,'awards':1,'patents':1,'projects':1,'url':1})
        if person is not None:
            person['id']=str(person['_id'])
            del person['_id']
            persons.append(person)
    with open('b.json','w+') as w:
        w.write(json.dumps(persons,ensure_ascii=False))

def crawl_person():
    #person_ids = ["5b9a33778d431508dea40be2", "5b9a33768d431508dea40be0", "5b9a33768d431508dea40bdf",
     #            "5b9a33788d431508dea40be6", "5b9a33788d431508dea40be7","5b9a33788d431508dea40be8","5b9a341e8d431508dea40ee0","5b9abce9c3666e23ba80d3da"]
    person_ids=["5baee78b8d431506855d34f0"]
    for id in person_ids:
        person = mongo_client.get_crawled_person_by_pid(id)
        crawl_person_info([person], None)

#crawl_person()
def get_data():
    data_list=[]
    with open('/Users/bcj/Documents/position_list.csv','r') as r:
        reader=csv.reader(r)
        for i ,data in enumerate(reader):
            data_list.append(data[0])
    with open('position_dict.json','w') as w:
        w.write(json.dumps(data_list,ensure_ascii=False))

#get_data()
def clear_status():
    persons=mongo_client.get_collection('uncrawled_person').find({'task_id':ObjectId('5bd58e9b8d431508e304d60a')})
    for person in persons:
        mongo_client.db['uncrawled_person'].update({'_id':person['_id']},{'$set':{"status":1}})
#clear_status()

#export_data()
# affs=mongo_client.db['aff'].find()
# for aff in affs:
#     print(aff['_id'])
#     if aff is not None and aff['domain'] !=" " :
#         print(aff['domain'])
#         domain_key=aff['domain'].split('.')[1]
#         print(domain_key)

# mongo_client=MongoDBClient()
# persons=mongo_client.db['crawled_person_final'].find()
# for p in persons:
#     if 'domain' in p:
#         mongo_client.db['crawled_person_final'].update({"_id":p['_id']},{'$rename':{'domain':'achieve'}})

def repeat():
    persons = mongo_client.get_crawled_person_by_taskId("5ba20fee8d4315163aba3cdd")
    for i, p in enumerate(persons):
        if 100>p['row_number'] > 0:
            p['_id'] = ObjectId(p['id'])
            p['task_id'] = ObjectId("5ba20fee8d4315163aba3cdd")
            p['result'] = sorted(p['result'], key=lambda s: s['last_time'], reverse=True)
            p['result'] = list(filter(select, p['result']))
            if len(p['result']) > 0:
                selected_item = p['result'][0]
                p['url'] = selected_item['url']
                p['source'] = 'crawler'
                p['info'] = crawl_mainpage.get_main_page(p['url'], p)
                print(p['_id'])
                print("{}-{}".format(p['name'], p['org']))
                print("url is****" + p['url'])
            if 'info' in p:
                p = apart_text(p)
            mongo_client.save_crawled_person(p)
#repeat()
def get_data():
    with open('/Users/bcj/Desktop/中国青年科技奖1-14届获得者名单-需添加数据-0926.csv','r') as f:
        datas=csv.reader(f)
        with open('/Users/bcj/Desktop/刘佳组数据.csv','w') as w:
            writer=csv.writer(w)
            for i,data in enumerate(datas):
                if i>1:
                    db_data=mongo_client.db['crawled_person_final'].find_one({'$and':[{'task_id':ObjectId("5ba903392bf7cb164b61af7e")},{'name':data[2]}]})
                    print(i)
                    if db_data is not None:
                        if 'url' in db_data:
                            data.append(db_data['url'])
                        else:
                            data.append("")
                        if 'aff' in db_data and 'inst' in db_data['aff']:
                            data.append(db_data['aff']['inst'])
                        else:
                            data.append("")
                        if 'position' in db_data:
                            data.append(db_data['position'])
                        else:
                            data.append("")
                        if 'honors' in db_data:
                            data.append(','.join(db_data['honors']))
                        else:
                            data.append("")
                        if 'awards_region' in db_data:
                            data.append(db_data['awards_region'])
                        else:
                            data.append("")
                        if 'academic_org_exp_region' in db_data:
                            data.append(db_data['academic_org_exp_region'])
                        else:
                            data.append("")
                        writer.writerow(data)
                    else:
                        writer.writerow(data)


#get_data()


def generate_data():
    persons=mongo_client.get_crawled_person_by_taskId("5baee7878d43156d04522d01")
    for person in persons:
        print(person['id'])
        if 'academic_org_exp_region' in person:
            person['academic_org_exp']=detail_apart.find_socs(strQ2B(person['academic_org_exp_region']))
            mongo_client.update_crawled_person_by_keyvalue(person['id'],'academic_org_exp',person['academic_org_exp'])
#generate_data()

def process_position():
    titles=set()
    datas=mongo_client.db['crawled_person_final'].find({ "academic_org_exp.title": {'$exists': True }},{'academic_org_exp.title':1})
    for data in datas:
        if 'academic_org_exp' in data:
            for t in data['academic_org_exp']:
                if 'title' in t and 1<len(re.sub('[\\d（）《》() \\n,，－-]','',t['title']))<6:
                    titles.add(re.sub('[\\d（）《》() \\n,，－-]','',t['title']))
    with open("/Users/bcj/Documents/科技部/EItools/EItools/classifier_mainpage/data/soc_position.json",'w') as w:
        json.dump(list(titles),w,ensure_ascii=False)

def test_crawl_person(id):
    person=mongo_client.get_crawled_person_by_pid(id)
    if person is not None:
        persons_info=crawl_service.crawl_person_info([person],None)
#test_crawl_person("5ba20fef8d431516f8316449")
def get_text_from_url(url):
    p={'name':"刘继峰"}
    p['info']=crawl_mainpage.get_main_page(url)
    print(p['info'])
    apart_text(p)

#get_text_from_url("http://people.ucas.ac.cn/~liujifeng")

def run_data():
    db=mongo_client.get_collection("crawled_person_final")
    db_url=mongo_client.get_collection("url2").find()
    for i,data in enumerate(db_url):
        if i<67:
            continue
        print(data)
        p=db.find_one({'_id':data['_id']})
        p['url']=data['url']
        p['info'] = crawl_mainpage.get_main_page(p['url'], p)
        if p['info']!="":
            p=apart_text(p)
            mongo_client.get_collection("url2").save(p)
#run_data()

#def test_award():
    # db = mongo_client.get_collection("crawled_person_final")
    # db_collection=db.find({'task_id':ObjectId("5ba20fee8d4315163aba3cdd")})
    # for data in db_collection:
    #     print(data['_id'])
    #     if 'patents_region' in data and data['patents_region'] !="":
    #         print(data['patents_region'])
    #         print(detail_apart.find_patents(data['patents_region']))
#test_award()

def find_awards():
    person=mongo_client.get_crawled_person_by_pid("5bcdc9438d43152c1b6c418e")
    if person is not None:
        print(detail_apart.find_awards(person['awards_region']))
#find_awards()

def caculate_data():
    persons=mongo_client.get_crawled_person("5bcea3b38d43152bf8876575")
    print(len(persons))
    count=0
    for person in persons:
        value=0
        if 'info' in person and person['info']!="":
            value+=1
        if 'edu_exp_region' in person and person['edu_exp_region']!="":
            value+=1
        if 'degree' in person and person['degree']!="":
            value+=1
        if 'exp_region' in person and person['exp_region']!="":
            value+=1
        if 'position' in person and person['position']!="":
            value+=1
        if 'title' in person and person['title']!="":
            value+=1
        if 'email' in person and person['email'] !="":
            value+=1
        if 'awards_region' in person and person['awards_region']!="":
            value+=1
        if 'patents_region' in person and person['patents_region']!="":
            value+=1
        if 'projects_region' in person and person['projects_region']!="":
            value+=1
        if 'pubs' in person and person['pubs'] is not None and len(person['pubs'])>0:
            value+=1
        if 'gender' in person and person['gender']!="":
            value+=1
        if value>7:
            count+=1
    print(count)
#caculate_data()

def select_website(r):
    return len(re.findall('ac\.cn|edu\.cn|cas\.cn|baike',r['url'] if 'url' in r else ""))>0 or len(re.findall('ac\.cn|edu\.cn|cas\.cn|baike',r['domain'] if 'domain' in r else ""))>0

def process1_data():
    task_id="5bcea3b38d43152bf8876575"
    persons=mongo_client.get_crawled_person(task_id)
    for i,person in enumerate(persons):
        if 1097<i<1099 or 0<0<465:
            result = person['result']
            result_rest = list(filter(select, result))
            result_rest = list(filter(select_website, result_rest))
            # for se in result_rest:
            #     se['last_time'] = crawl_mainpage.get_lasttime_from_mainpage(se['url'])
            result_sorted_final = sorted(result_rest, key=lambda s: s['last_time'], reverse=True)
            if len(result_sorted_final) > 0:
                selected_item = result_sorted_final[0]
                if selected_item['url']!=person['url']:
                    print(i)
                    person['result']=result_sorted_final
                    person['url'] = selected_item['url']
                    person['source'] = 'crawler'
                    person['info'] = crawl_mainpage.get_main_page(person['url'], person)
                    crawl_service.crawl_person_info([person], task_id)
#process1_data()


def get():
    person=mongo_client.get_crawled_person_by_pid("5bcea4a68d4315560edcf16b")


#get()
def find_longest(li):
    nums = [len(x) for x in li]
    max_num_index_list = map(nums.index, heapq.nlargest(2, nums))
    return [li[x] for x in list(max_num_index_list)]

def gen_data():
    with open('/Users/bcj/Desktop/data(1000条).json','r') as f:
        datas=json.load(f)
    with open('/Users/bcj/Desktop/data3(1000条).json','w') as w:
        for i,data in enumerate(datas):
            # data['awards']=detail_apart.find_awards_list([data['awards_region']])
            # patents=[]
            # for d in data['patents']:
            #     d['title']=find_longest(d['title'])[0]
            #     d['code']=find_longest(re.sp)
            #     d['code']=re.sub('[\(\)（）]','',d['code'])
            #     if len(d['title'])>4:
            #         patents.append(d)
            #data['patents']=patents
            del data['patents_region']
            del data['awards_region']
            del data['projects_region']
            del data['edu_exp_region']
            del data['exp_region']
            if 'status' in data:
                del data['status']
            del data['row_number']
            del data['academic_org_exp_region']

        w.write(json.dumps(datas,ensure_ascii=False))
#gen_data()

def open_file():
    with open('/Users/bcj/Desktop/data_final(1000条).json','r') as f:
        datas=json.load(f)
    with open('/Users/bcj/Desktop/test_data.csv','w') as w:
        writer=csv.writer(w)
        for data in datas:
            writer.writerow([data['name']])
#open_file()

def process_data_title():
    persons=mongo_client.get_crawled_person_all_data_by_taskId("5bd58e9b8d431508e304d60a")
    for p in persons:
        p=mongo_client.get_crawled_person_by_pid(p['id'])
        p['title'] = ""
        if 'info' in p:


process_data_title()








































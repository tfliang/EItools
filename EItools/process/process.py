import csv
import json
import string

import re

from MagicBaidu import MagicBaidu
from MagicGoogle import MagicGoogle
from bson import ObjectId

from EItools.client.mongo_client import MongoDBClient
from EItools.crawler.crawl_information import crawl_person_info

mongoClient=MongoDBClient()
def process_data():
    collection_person=mongoClient.db['crawled_person_final'].find()
    for i,p in enumerate(collection_person):
        print(i)
        if 'is_new_aff' in p and p['is_new_aff']==1:
            aff=p['ini'].split(',')[1]
            record=True
            for c_aff in p['current-aff']:
                if c_aff.find(aff) !=-1 or aff.find(c_aff) !=-1:
                    record=False
                    break
            mongoClient.db['crawled_person_final'].update({'_id':p['_id']},{'$set':{'change':record}})

#process_data()
def write_csv():
    collection_person = mongoClient.db['crawled_person_final'].find({'change':True})
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
                    person=mongoClient.db['crawled_person_final'].find_one({'_id':ObjectId(id)})
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
mongo_client=MongoDBClient()
PROXIES = [{
    'http': 'http://159.203.174.2:3128'
}]

mg = MagicGoogle(PROXIES)
mb = MagicBaidu()


def get_res(query):
    res = []
    try:
        for i in mb.search(query=query, pause=0.5):
            if 'baike.com' in i['domain'] or 'baidu.com' in i['domain']:
                continue
            if '官网' in i['title'] :
                print(i)
                if 'domain' in i:
                    #result=re.split('-',i['domain'])
                    return i['domain']
            else:
                return i['domain']
    except Exception as e:
        return ""

def get_domain():
    institutions=mongo_client.db['institution'].find()
    for inst in institutions:
        if inst['domain'] is None or 'baidu.com' in inst['domain'] or 'baike.com' in inst['domain']:
            name=inst['name']
            print(name)
            result=get_res(name)
            print(result)
            inst['domain']=result
            mongo_client.db['institution'].save(inst)
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

person=mongo_client.get_crawled_person_by_pid("5b8676c98d431526a3507939")
crawl_person_info([person], None)






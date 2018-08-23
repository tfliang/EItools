import csv
import string

import re

from bson import ObjectId

from EItools.client.mongo_client import MongoDBClient

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











import csv
import json

from bson import ObjectId

from EItools.client.mongo_client import MongoDBClient

mongo_client=MongoDBClient()
def export():
    persons=[]
    j=0
    with open("/Users/bcj/Desktop/part_data_{}.json".format('current_aff'),'w',encoding='utf-8') as w:
        with open("/Users/bcj/Desktop/更新用.csv",'r',encoding='utf-8') as f:
           csv_file=csv.reader(f)
           for i,item in enumerate(csv_file):
                if i>=0 and i<40000:
                    print(i)
                    name=item[0]
                    org=item[1]
                    person=mongo_client.db['crawled_person_final'].find_one({"ini":name+","+org})
                    j=j+1
                    if person is None:
                        print(name + " " + org)
                    if  person is not None and 'pos' not in person:
                        # del person['_id']
                        # if 'taskId' in person:
                        #     del person['taskId']
                        # if 'res' in person:
                        #     del person['res']
                        # if 'query' in person:
                        #     del person['query']
                        # if 'ini' in person:
                        #     del person['ini']
                        # if 'PER' in person:
                        #     del person['PER']
                        # if 'ADR' in person:
                        #     del person['ADR']
                        # if 'status' in person:
                        #     del person['status']
                        # if 'source' in person:
                        #     del person['source']
                        mongo_client.db['crawled_person_final'].update({"_id":person['_id']},{'$set':{'pos':i+1}})
                        #persons.append(person)
        print("total: {}".format(j))
        #json.dump(persons,w,ensure_ascii=False)

#export()
def buchong():
    all_persons=mongo_client.db['buchong'].find()
    j=0
    with open('a.txt','w+') as f:
        for person in all_persons:
            p_c=mongo_client.db['search'].find_one({"_id":person['_id']})
            if p_c is not None:
                j=j+1
                print(person['_id'])
                f.write(str(person['_id']))
                mongo_client.db['search'].remove({"_id": person['_id']})
                mongo_client.db['search'].save(person)
        print(j)

#buchong()

def extract():
    import requests
    from bs4 import BeautifulSoup
    import pextract as pe

    url = 'http://sfst.ncu.edu.cn/News_View.asp?NewsID=136'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    html, pval = pe.extract(soup, text_only=False, remove_img=False)
    text, pval = pe.extract(soup)
    print(pval)  # This is a strong feature for web page classification
    with open('out.html', 'w', encoding='utf-8') as f:
        f.write(html)
    with open('out.txt', 'w', encoding='utf-8') as f:
        f.write(text)

#extract()
mongo_client=MongoDBClient()
persons=mongo_client.db['crawled_person_final'].find()
for i,p in enumerate(persons):
    print(i)
    if 'domain' in p:
        mongo_client.db['crawled_person_final'].update({"_id":p['_id']},{'$rename':{'domain':'achieve'}})

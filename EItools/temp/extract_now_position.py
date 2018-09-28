import re

from EItools.client.mongo_client import MongoDBClient

mongoClient=MongoDBClient()

def get_current_position_from_person():
    persons=mongoClient.db['crawled_person_final'].find().skip(0).limit(15000)
    print(persons.count())
    for p in persons:
        a=p['ini'].split(',')[1]
        print(p['_id'])
        if 'info' in p:
            info=p['info']
        else:
            info=""
        current_aff=[]
        if 'AFF' in p :
            for aff in p['AFF'] :
                print("aff-{}".format(aff))
                try:
                    aff_filter=aff.replace('(','\(').replace(')','\)').replace('[','\[').replace(']','\]').replace('+','\+').replace('\\r','\\\\r')
                    pattern='((现为)|(至今)|(现任职于)|(现任)|(-今于)|(目前为)|(现为)|(工作单位)|(-今)){1,2}[\s\S]{0,5}'+aff_filter
                    print("pattern-{}".format(pattern))
                    result=re.search(pattern,info)
                    if result is not None:
                        current_aff.append(aff)
                    else:
                        pattern_back = aff_filter + '[\s\S]{0,5}((至今)){1,2}'
                        result = re.search(pattern_back,info)
                        if result is not None:
                            current_aff.append(aff)
                except Exception as e:
                    print(e)
        # if len(current_aff)==0:
        #     current_aff.append(a)
            #print("info-{}".format(p['info']))
            #print("current-aff-{}".format(current_aff))
            if len(current_aff)>0:
                mongoClient.db['crawled_person_final'].update({"_id":p['_id']},{"$set":{"is_new_aff":1}})
            else:
                mongoClient.db['crawled_person_final'].update({"_id": p['_id']}, {"$set": {"is_new_aff": 0}})
            #mongoClient.db['crawled_person_final'].update({"_id":p['_id']},{"$set":{"current-aff":current_aff}})
        else:
            mongoClient.db['crawled_person_final'].update({"_id": p['_id']}, {"$set": {"is_new_aff": 0}})
get_current_position_from_person()

def caculate():
    persons=mongoClient.db['crawled_person_final'].find()
    print(persons.count())
    i=0
    for p in persons:
       a = p['ini'].split(',')[1]
       print(a)
       if 'current-aff' in p and len(p['current-aff'])>0:
           i=i+1
       if 'current-aff' not in p or len(p['current-aff']) == 0:
           p['current-aff']=[]
           p['current-aff'].append(a)
           mongoClient.db['crawled_person_final'].update({"_id": p['_id']}, {"$set": {"current-aff": p['current-aff']}})
    print(i)

#caculate()


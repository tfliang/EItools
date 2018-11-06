import pymongo
import re
from bson import ObjectId
from pymongo import MongoClient

from EItools.client import settings
from EItools.model.task import Task

class MongoDBClient(object):
    def __init__(self, host=settings.MONGO_HOST, port=settings.MONGO_PORT):
        self.client = MongoClient(host, port,connect=False)

    def get_collection(self,collection_name,db_name=settings.MONGO_DBNAME,user=settings.MONGO_USERNAME, password=settings.MONGO_PASSWORD):
        self.db = self.client[db_name]
        if password is not None and password != "":
            self.db.authenticate(user, password)
        # self.get_collection(settings.MONGO_UNCRAWLED_PERSON) = self.db[settings.MONGO_UNCRAWLED_PERSON]
        # self.get_collection(settings.MONGO_CRAWLED_PERSON) = self.db[settings.MONGO_CRAWLED_PERSON]
        # self.pub_col = self.db["publication_dupl"]
        # self.ins_col = self.db["institution"]
        # self.proj_col = self.db["project"]
        # self.patent_col = self.db["patent"]
        # self.get_collection(settings.MONGO_ALL_TASK) = self.db[settings.MONGO_ALL_TASK]
        self.col=self.db[collection_name]
        return self.col

    #task function
    def get_all_task(self,offset=0,size=0):
        tasks_info = []
        if size > 0 and offset >= 0:
            tasks= self.get_collection(settings.MONGO_ALL_TASK).find().sort("publish_time",pymongo.DESCENDING).skip(offset).limit(size)
        else:
            tasks = self.get_collection(settings.MONGO_ALL_TASK).find()
        for item in tasks:
            item['id'] = str(item['_id'])
            del item['_id']
            tasks_info.append(item)
        return tasks_info

    def get_task_count(self):
        return self.get_collection(settings.MONGO_ALL_TASK).find().count()

    def get_unfinished_task(self):
        task_ids=[]
        tasks=self.get_collection(settings.MONGO_ALL_TASK).find({"$or":[{"status": 1},{"status":3}]})
        for item in tasks:
            task_ids.append(str(item["_id"]))
            self.update_task(2,str(item['_id']))
        return task_ids

    def get_doing_task(self):
        task_ids=[]
        tasks=self.get_collection(settings.MONGO_ALL_TASK).find({"$or":[{"status": 2}]})
        for item in tasks:
            task_ids.append(item["_id"])
        return task_ids

    def save_task(self, item):
        task=Task(item)
        task.save()

    def update_task(self, status, id):
        self.get_collection(settings.MONGO_ALL_TASK).update({"_id": ObjectId(id)}, {"$set": {"status": status}})


    def get_task_by_Id(self, id):
        try:
            task=self.get_collection(settings.MONGO_ALL_TASK).find_one({"_id": ObjectId(id)})
            task['id']=str(task['_id'])
            del task['_id']
            return task
        except Exception as e:
            return None

    # person by taskId function
    def get_person_by_taskId(self, id, offset=0, size=0):
        persons = []
        for item in (self.get_collection(settings.MONGO_UNCRAWLED_PERSON).find({"task_id": ObjectId(id)})):
            persons.append(item)
        if size > 0 and offset >= 0:
            return persons[offset:offset + size]
        else:
            return persons

    def get_uncrawled_person_by_taskId(self, id, offset=0, size=0):
        persons = []
        c=self.get_collection(settings.MONGO_UNCRAWLED_PERSON).find({"task_id": ObjectId(id)})
        if size > 0 and offset >= 0:
            c=c.skip(offset).limit(size)
        for item in c:
            item['id'] = str(item['_id'])
            item['task_id']=str(item['task_id'])
            if 'status' not in item or item['status'] != 0:
                del item['_id']
                #del item['task_id']
                persons.append(item)
        return persons

    def get_crawled_person_by_taskId(self,id,offset=0, size=0,fields=[]):
        persons = []
        c = self.get_collection(settings.MONGO_CRAWLED_PERSON).find({"task_id": ObjectId(id)})
        if size > 0 and offset >= 0:
            c = c.skip(offset).limit(size)
        for person in c:
            person_simple = {}
            person_simple['id'] = str(person['_id'])
            del person['_id']
            del person['task_id']
            person_simple['status'] = 1
            person_simple['name'] = person['name'] if 'name' in person else ""
            person_simple['org'] = person['org'] if 'org' in person else ""
            person_simple['gender'] = person['gender'] if 'gender' in person else ""
            person_simple['email'] = person['email'] if 'email' in person else ""
            person_simple['position'] = person['position'] if 'position' in person else ""
            person_simple['h_index'] = person['h_index'] if 'h_index' in person else ""
            person_simple['citation'] = person['citation'] if 'citation' in person else ""
            person_simple['emails_prob']=person['emails_prob'] if 'emails_prob'in person else []
            person_simple['changed'] = person['changed'] if 'changed' in person else False
            persons.append(person_simple)
        return persons

    def get_crawled_person_all_data_by_taskId(self,id, offset=0, size=0):
        persons = []
        c = self.get_collection(settings.MONGO_CRAWLED_PERSON).find({"task_id": ObjectId(id)})
        if size > 0 and offset >= 0:
            c = c.skip(offset).limit(size)
        for person in c:
            person['id']=str(person['_id'])
            person['task_id']=str(person['task_id'])
            del person['_id']
            persons.append(person)
        return persons

    def search_crawled_person_by_taskId(self,id,name,offset=0,size=0):
        persons = []
        c = self.get_collection(settings.MONGO_CRAWLED_PERSON).find({'$and':[{"task_id": ObjectId(id)},{"name":re.compile(name)}]})
        if size > 0 and offset >= 0:
            c = c.skip(offset).limit(size)
        for item in c:
            item['id'] = str(item['_id'])
            del item['_id']
            del item['task_id']
            persons.append(item)
        return persons

    def search_crawled_person_num_by_taskId(self, id,name):
        return self.get_collection(settings.MONGO_CRAWLED_PERSON).find({'$and':[{"task_id": ObjectId(id)},{"name":re.compile(name)}]}).count()

    def get_crawled_person_num_by_taskId(self, id):
        return self.get_collection(settings.MONGO_CRAWLED_PERSON).find({"$and": [{"task_id": ObjectId(id)}]}).count()

    def get_crawled_person(self, id,offset=0, size=0):
        persons = []
        c = self.get_collection(settings.MONGO_CRAWLED_PERSON).find({"task_id": ObjectId(id)})
        if size > 0 and offset >= 0:
            c = c.skip(offset).limit(size)
        return c

    def get_person_num_by_taskId(self, id):
        return self.get_collection(settings.MONGO_UNCRAWLED_PERSON).find({"$and": [{"task_id": ObjectId(id)},{"status":{'$ne':0}}]}).count()

    def get_person(self, pid):
        return self.get_collection(settings.MONGO_UNCRAWLED_PERSON).find_one({"_id": ObjectId(pid)})

    def get_crawled_person_by_pid(self,pid):
        return self.get_collection(settings.MONGO_CRAWLED_PERSON).find_one({"_id":ObjectId(pid)})

    def get_changeinfo_list(self,id=None,offset=0,size=0):
        if id is not None:
            c = self.get_collection(settings.MONGO_CRAWLED_PERSON).find({'$and':[{"changed": True},{"_id":ObjectId(id)}]},{'change_info':1,'task_id':1,'_id':1,'name':1})
        else:
            c=self.get_collection(settings.MONGO_CRAWLED_PERSON).find({"changed":True},{'change_info':1,'task_id':1,'_id':1,'name':1})
        if size>0 and offset>=0:
            c=c.skip(offset).limit(size)
        persons=[]
        for i,person in enumerate(c):
            person['id']=str(person['_id'])
            person['task_id']=str(person['task_id'])
            task=self.get_task_by_Id(person['task_id'])
            person['task_name']=task['task_name']
            person['changed']=person['changed'] if 'changed' in person else False
            del person['_id']
            persons.append(person)
        return persons

    def search_changeinfo_list(self,name=None,offset=0,size=0):
        if name is not None:
            c = self.get_collection(settings.MONGO_CRAWLED_PERSON).find({'$and':[{"changed": True},{"name":re.compile(name)}]},{'change_info':1,'task_id':1,'_id':1,'name':1})
        else:
            c=self.get_collection(settings.MONGO_CRAWLED_PERSON).find({"changed":True},{'change_info':1,'task_id':1,'_id':1,'name':1})
        if size>0 and offset>=0:
            c=c.skip(offset).limit(size)
        persons=[]
        for i,person in enumerate(c):
            person['id']=str(person['_id'])
            person['task_id']=str(person['task_id'])
            task=self.get_task_by_Id(person['task_id'])
            person['task_name']=task['task_name']
            person['changed']=person['changed'] if 'changed' in person else False
            del person['_id']
            persons.append(person)
        return persons
    def search_changeinfo_list_num(self,name):
        return self.get_collection(settings.MONGO_CRAWLED_PERSON).find({'$and':[{"changed": True},{"name":re.compile(name)}]}).count()

    def get_changeinfo_num(self):
        return self.get_collection(settings.MONGO_CRAWLED_PERSON).find({"changed": 'true'}).count()

    def save_person(self, item):
        self.get_collection(settings.MONGO_UNCRAWLED_PERSON).save(item)

    def rm_person_by_id(self, pid):
        self.get_collection(settings.MONGO_UNCRAWLED_PERSON).remove({"_id": pid})

    def update_person_by_id(self,person_id,task_id):
        self.get_collection(settings.MONGO_UNCRAWLED_PERSON).update({"_id":ObjectId(person_id)},{"$set":{"status":0}})
        self.get_collection(settings.MONGO_ALL_TASK).update({"_id":ObjectId(task_id)},{"$inc":{"has_finished":1}})

    def update_person_by_keyvalue(self,person_id,key,value):
        self.get_collection(settings.MONGO_UNCRAWLED_PERSON).update({"_id": ObjectId(person_id)}, {"$set": {key: value}})

    def update_crawled_person_by_keyvalue(self, person_id, key, value):
        self.get_collection(settings.MONGO_CRAWLED_PERSON).update({"_id": ObjectId(person_id)}, {"$set": {key: value}})

    def is_crawled_person(self, name,org):
        return self.get_collection(settings.MONGO_CRAWLED_PERSON).find({"$and":[{"name": name},{"org": org}]}).count()>0

    def get_person_by_nameandorg(self, name,org):
        return self.get_collection(settings.MONGO_CRAWLED_PERSON).find_one({"$and":[{"name": name},{"org": org}]})

    def save_crawled_person(self,item):
        self.get_collection(settings.MONGO_CRAWLED_PERSON).save(item)

    def update_crawled_person_status(self,id):
        self.get_collection(settings.MONGO_CRAWLED_PERSON).update({"_id":ObjectId(id)},{"$set":{"status":0}})

mongo_client = MongoDBClient()


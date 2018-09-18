from bson import ObjectId
from pymongo import MongoClient

from EItools.client import settings


class MongoDBClient(object):
    def __init__(self, host=settings.MONGO_HOST, port=settings.MONGO_PORT, db_name=settings.MONGO_DBNAME,
                 user=settings.MONGO_USERNAME, password=settings.MONGO_PASSWORD):
        self.client = MongoClient(host, port,connect=False)
        self.db = self.client[db_name]
        if password is not None and password !="":
            self.db.authenticate(user, password)
        self.person_col = self.db[settings.MONGO_UNCRAWLED_PERSON]
        self.crawed_person_col = self.db[settings.MONGO_CRAWLED_PERSON]
        self.pub_col = self.db["publication_dupl"]
        self.ins_col = self.db["institution"]
        self.proj_col = self.db["project"]
        self.patent_col = self.db["patent"]
        self.task_col = self.db[settings.MONGO_ALL_TASK]

    #task function
    def get_all_task(self,offset=0,size=0):
        tasks_info = []
        if size > 0 and offset >= 0:
            tasks= self.task_col.find().sort({'publish_time':-1}).skip(offset).limit(size)
        else:
            tasks = self.task_col.find()
        for item in tasks:
            item['id'] = str(item['_id'])
            del item['_id']
            tasks_info.append(item)
        return tasks_info

    def get_task_count(self):
        return self.task_col.find().count()

    def get_unfinished_task(self):
        task_ids=[]
        tasks=self.task_col.find({"$or":[{"status": 1},{"status":3}]})
        for item in tasks:
            task_ids.append(str(item["_id"]))
            self.update_task(2,str(item['_id']))
        return task_ids

    def get_doing_task(self):
        task_ids=[]
        tasks=self.task_col.find({"$or":[{"status": 2}]})
        for item in tasks:
            task_ids.append(item["_id"])
        return task_ids

    def save_task(self, item):
        self.task_col.save(item)

    def update_task(self, status, id):
        self.task_col.update({"_id": ObjectId(id)}, {"$set": {"status": status}})


    def get_task_by_Id(self, id):
        try:
            task=self.task_col.find_one({"_id": ObjectId(id)})
            task['id']=str(task['_id'])
            del task['_id']
            return task
        except Exception as e:
            return None

    # person by taskId function
    def get_person_by_taskId(self, id, offset=0, size=0):
        persons = []
        for item in (self.person_col.find({"task_id": ObjectId(id)})):
            persons.append(item)
        if size > 0 and offset >= 0:
            return persons[offset:offset + size]
        else:
            return persons

    def get_uncrawled_person_by_taskId(self, id, offset=0, size=0):
        persons = []
        c=self.person_col.find({"task_id": ObjectId(id)})
        if size > 0 and offset >= 0:
            c=c.skip(offset).limit(size)
        for item in c:
            item['id'] = str(item['_id'])
            if 'status' not in item or item['status'] != 0:
                #del item['_id']
                #del item['task_id']
                persons.append(item)
        return persons

    def get_crawled_person_by_taskId(self,id, offset=0, size=0):
        persons = []
        c = self.crawed_person_col.find({"task_id": ObjectId(id)})
        if size > 0 and offset >= 0:
            c = c.skip(offset).limit(size)
        for item in c:
            item['id'] = str(item['_id'])
            del item['_id']
            del item['task_id']
            persons.append(item)
        return persons

    def get_crawled_person_num_by_taskId(self, id):
        return self.crawed_person_col.find({"$and": [{"task_id": ObjectId(id)}]}).count()

    def get_crawled_person(self,  offset=0, size=0):
        persons = []
        c = self.crawed_person_col.find()
        if size > 0 and offset >= 0:
            c = c.skip(offset).limit(size)
        for item in c:
            item['id'] = str(item['_id'])
            persons.append(item['id'])
        return persons

    def get_person_num_by_taskId(self, id):
        return self.person_col.find({"$and": [{"task_id": ObjectId(id)},{"status":{'$ne':0}}]}).count()


    #person function

    def get_person(self, pid):
        return self.person_col.find_one({"_id": ObjectId(pid)})
    def get_crawled_person_by_pid(self,pid):
        print(self.crawed_person_col.find_one({"_id":ObjectId(pid)}))
        return self.crawed_person_col.find_one({"_id":ObjectId(pid)})

    def save_person(self, item):
        self.person_col.save(item)

    def rm_person_by_id(self, pid):
        self.person_col.remove({"_id": pid})

    def update_person_by_id(self,person_id,task_id):
        self.person_col.update({"_id":ObjectId(person_id)},{"$set":{"status":0}})
        self.task_col.update({"_id":ObjectId(task_id)},{"$inc":{"has_finished":1}})

    def update_person_by_keyvalue(self,person_id,key,value):
        self.person_col.update({"_id": ObjectId(person_id)}, {"$set": {key: value}})

    def update_crawled_person_by_keyvalue(self, person_id, key, value):
        print(key)
        print(value)
        self.crawed_person_col.update({"_id": ObjectId(person_id)}, {"$set": {key: value}})

    def is_crawled_person(self, name,org):
        return self.crawed_person_col.find({"$and":[{"name": name},{"org": org}]}).count()>0

    def get_person_by_nameandorg(self, name,org):
        return self.crawed_person_col.find_one({"$and":[{"name": name},{"org": org}]})

    def save_crawled_person(self,item):
        self.crawed_person_col.save(item)

    def update_crawled_person_status(self,id):
        self.crawed_person_col.update({"_id":ObjectId(id)},{"$set":{"status":0}})

    def update_person_projects(self, pid, projects):
        p_item = self.get_person(pid)
        p_item["projs"] = projects
        self.person_col.save(p_item)
        self.ins_col.remove(ObjectId(p_item["_id"]))

    def get_patent(self, pid):
        return self.patent_col.find_one({"_id": ObjectId(pid)})

    def get_project(self, pid):
        return self.proj_col.find_one({"_id": ObjectId(pid)})

    def get_pub(self, pid):
        return self.pub_col.find_one({"_id": ObjectId(pid)})

    def save_pub(self, item):
        self.pub_col.save(item)


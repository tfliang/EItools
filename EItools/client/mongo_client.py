from bson import ObjectId
from pymongo import MongoClient

from EItools.client import settings


class MongoDBClient(object):
    def __init__(self, host=settings.MONGO_HOST, port=settings.MONGO_PORT, db_name=settings.MONGO_DBNAME,
                 user=settings.MONGO_USERNAME, password=settings.MONGO_PASSWORD):
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        if password is not None:
            self.db.authenticate(user, password)
        self.person_col = self.db["person_uncrawled"]
        self.pub_col = self.db["publication_dupl"]
        self.ins_col = self.db["institution"]
        self.proj_col = self.db["project"]
        self.patent_col = self.db["patent"]
        self.task_col = self.db["task"]

    def get_crawl_info(self):
        return self.db["crawled_person"]
    def get_test_person(self):
        return self.db["tech_person"].find()

    def get_test_person_info(self,offset,size):
        return self.db["tech_person"].find().skip(offset).limit(size)
    def get_person(self, pid):
        return self.person_col.find_one({"_id": ObjectId(pid)})

    def save_person(self, item):
        self.person_col.save(item)
    def get_person_by_taskId(self,id):
        persons=[]
        for item in (self.person_col.find({"taskId": ObjectId(id)})):
            persons.append(item)
        return persons

    def save_task(self, item):
        self.task_col.save(item)

    def update_task(self, status,id):
        self.task_col.update({"status":status},{"_id":ObjectId(id)})

    def get_ins(self, iid):
        return self.ins_col.find_one({"_id": ObjectId(iid)})

    def get_ins_member(self, iid):
        faculties = self.person_col.find(
            {"$or": [{"work.aff.inst.i": ObjectId(iid)}, {"work.aff.dept.i": ObjectId(iid)}]})
        return faculties

    def count_ins_member(self, iid):
        n_faculty = self.person_col.count({"work.aff.dept.i": ObjectId(iid)})
        return n_faculty

    def set_ins_parent(self, iid, pid):
        ins = self.ins_col.find_one({"_id": ObjectId(iid)})
        if ins is not None:
            ins["parent"] = ObjectId(pid)
        self.ins_col.save(ins)

    def update_ins_stat(self, iid, stat):
        ins = self.ins_col.find_one({"_id": ObjectId(iid)})
        if ins is not None:
            ins["stat"] = stat
        self.ins_col.save(ins)

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

    def get_depts(self, iid):
        depts = []
        for item in self.ins_col.find({"parent": ObjectId(iid)}):
            if not item["is_removed"]:
                depts.append(str(item["_id"]))
        return depts

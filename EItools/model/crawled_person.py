from mongoengine import Document, StringField, IntField, ObjectIdField, ListField, EmbeddedDocumentField, \
    EmbeddedDocument, connect
from peewee import DoubleField

from EItools.common.db_base import DBBase

from EItools.common.connection import *

class crawl_result(EmbeddedDocument):
    title=StringField()
    url=StringField()
    domain=StringField()
    text=StringField()
    source=StringField()
    label=IntField()
    score=DoubleField()
    last_time=IntField()

class edu(EmbeddedDocument):
    start=StringField()
    end=StringField()
    diploma=StringField()
    degree=StringField()
    inst=StringField()
    country=StringField()

class exp(EmbeddedDocument):
    position=StringField()
    inst=StringField()

class academic_org_exp(EmbeddedDocument):
    title=StringField()
    org=StringField()
    duration=StringField()

class award(EmbeddedDocument):
    title=StringField()
    year=StringField()
    award=StringField()

class patent(EmbeddedDocument):
    title=StringField()
    inventors=StringField()
    issue_data=StringField()
    issue_by=StringField()
    code=StringField()
    ipc=StringField()

class project(EmbeddedDocument):
    code=StringField()
    title=StringField()
    role=StringField()
    cat=StringField()
    fund=StringField()
    start=StringField()
    end=StringField()


class pub(EmbeddedDocument):
    title=StringField()
    authors=StringField()
    venue=StringField()
    volume=StringField()

class crawled_person (Document):
    _id=ObjectIdField()
    name=StringField()
    org=StringField()
    task_id=ObjectIdField()
    h_index=IntField()
    citation=IntField()
    status=IntField()  #0 完成
    result=ListField(EmbeddedDocumentField(crawl_result))
    url=StringField()
    source=StringField()
    info=StringField()
    birth_time=StringField()
    mobile=StringField()
    degree=StringField()
    diploma=StringField()
    honors=ListField(StringField())
    title=StringField()
    position=StringField()
    research=StringField()
    gender=StringField()
    email=StringField()
    edu_exp_region = StringField()
    exp_region = StringField()
    academic_org_exp_region = StringField()
    awards_region = StringField()
    patents_region = StringField()
    projects_region = StringField()
    edu_exp=ListField(EmbeddedDocumentField(edu))
    exp=ListField(EmbeddedDocumentField(exp))
    awards=ListField(EmbeddedDocumentField(award))
    patents=ListField(EmbeddedDocumentField(patent))
    projects=ListField(EmbeddedDocumentField(project))
    pubs = ListField(EmbeddedDocumentField(pub))





class crawled_person_opt(DBBase):
    def __init__(self):
        super(crawled_person_opt,self).__init__(crawled_person)
    def get_crawled_person_by_taskId(self,id,offset=0,size=0):
        field_dict={
            'status': 1,
            'name': 1,
            'org': 1,
            'gender': 1,
            'email': 1,
            'position':1,
            'h_index':1,
            'citation':1
        }
        crawled_persons=self.get({"task_id":id})
        return crawled_persons

# c_l_o=crawled_person_opt()
# print(c_l_o.get_crawled_person_by_taskId(ObjectIdField("5bcdc78a8d43152bf8876574")))















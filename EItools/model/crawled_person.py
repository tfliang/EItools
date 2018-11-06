from mongoengine import Document, StringField, IntField, ObjectIdField, ListField, EmbeddedDocumentField, \
    EmbeddedDocument, connect
from mongoengine.context_managers import switch_db
from peewee import DoubleField

from EItools.common.db_base import DBBase

from EItools.common.connection import *

class Crawl_result(EmbeddedDocument):
    title=StringField()
    url=StringField()
    domain=StringField()
    text=StringField()
    source=StringField()
    label=IntField()
    score=DoubleField()
    last_time=IntField()

class Edu(EmbeddedDocument):
    start=StringField()
    end=StringField()
    diploma=StringField()
    degree=StringField()
    inst=StringField()
    country=StringField()

class Exp(EmbeddedDocument):
    position=StringField()
    inst=StringField()
    end=StringField()
    start=StringField()

class Academic_org_exp(EmbeddedDocument):
    title=StringField()
    org=StringField()
    duration=StringField()

class Award(EmbeddedDocument):
    title=StringField()
    year=StringField()
    award=StringField()

class Patent(EmbeddedDocument):
    title=StringField()
    inventors=StringField()
    issue_date=StringField()
    issue_by=StringField()
    code=StringField()
    ipc=StringField()

class Project(EmbeddedDocument):
    code=StringField()
    title=StringField()
    role=StringField()
    cat=StringField()
    fund=StringField()
    start=StringField()
    end=StringField()


class Pub(EmbeddedDocument):
    title=StringField()
    authors=StringField()
    venue=StringField()
    volume=StringField()

    source=StringField()
    count=IntField()
    label=StringField()
    author=StringField()
    year=IntField()

class Aff(EmbeddedDocument):
    inst=StringField()
    dept=StringField()

class Academic_org_exp(EmbeddedDocument):
    org=StringField()
    title=StringField()
    duration=StringField()




class Crawled_person(Document):
    meta = {
        'collection': 'crawled_person_final',
    }
    _id=ObjectIdField()
    name=StringField()
    org=StringField()
    task_id=ObjectIdField()
    h_index=IntField()
    citation=IntField()
    status=IntField()  #0 完成
    result=ListField(EmbeddedDocumentField(Crawl_result))
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

    edu_exp=ListField(EmbeddedDocumentField(Edu))
    exp=ListField(EmbeddedDocumentField(Exp))
    academic_org_exp=ListField(EmbeddedDocumentField(Academic_org_exp))
    awards=ListField(EmbeddedDocumentField(Award))
    patents=ListField(EmbeddedDocumentField(Patent))
    projects=ListField(EmbeddedDocumentField(Project))
    pubs = ListField(EmbeddedDocumentField(Pub))

    emails_prob = ListField()
    achieve = StringField()
    result = ListField()
    row_number=IntField()
    aff=EmbeddedDocumentField(Aff)






class Crawled_person_opt(DBBase):
    def __init__(self):
        super(Crawled_person_opt,self).__init__(Crawled_person)


    def get_crawled_person(self,data,offset=0,size=0,part="all"):
        if part=="list":

            crawled_persons=self.get(data,offset=offset,size=size).fields(_id = 1, status = 1, name = 1, org = 1, gender = 1,email=1,position=1,h_index=1,citation=1,task_id=1)\
                                         .to_json(ensure_ascii=False)
        elif part=="dowload":
            crawled_persons = self.get(data, offset=offset, size=size).fields(_id=1,name=1,org=1,task_id=1,h_index=1,citation=1,status=1,url=1,source=1,birth_time=1,mobile=1,degree=1,
                                                                              diploma=1,honors=1,title=1,position=1,research=1,gender=1,email=1,edu_exp=1,exp=1,academic_org_exp=1,awards=1,
                                                                              patents=1,projects=1,pubs=1,achieve=1,row_number=1,aff=1)\
                .to_json(ensure_ascii=False)
        elif part=="one":
            crawled_persons = self.get(data, offset=offset, size=size).exclude("result").exclude("info").\
                to_json(ensure_ascii=False)
        else:
            crawled_persons = self.get(data, offset=offset, size=size).\
                to_json(ensure_ascii=False)
        return crawled_persons



    def get_count(self,data):
        return self.get_count(data)

    def save_crawled_person(self,data):
        return self.add(data)




















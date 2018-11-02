from mongoengine import Document, StringField, IntField, ObjectIdField, ListField, EmbeddedDocumentField, \
    EmbeddedDocument, connect
from peewee import DoubleField



connect('project1', host='mongodb://localhost:27017/test_database')
class crawled_person (Document):
    _id=ObjectIdField()
    name=StringField()
    org=StringField()
    task_id=ObjectIdField()
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









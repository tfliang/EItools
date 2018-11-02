from mongoengine import StringField, Document, IntField


class uncrawled_person(Document):
    name=StringField()
    org=StringField()
    task_id=StringField()
    status=IntField()


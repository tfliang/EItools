from mongoengine import Document, StringField, IntField,ObjectIdField


class Task (Document):
    _id=ObjectIdField()
    task_name=StringField()
    creator_name=StringField()
    creator_id=StringField()
    publish_time=StringField()
    file_name=StringField()
    status=IntField()
    total=IntField()
    has_finished=IntField()
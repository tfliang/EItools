from mongoengine import Document, StringField, IntField,ObjectIdField

from EItools.common.db_base import DBBase


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

class Task_opt(DBBase):
    def __init__(self):
        super(Task_opt,self).__init__(Task)


    def get_task(self,data,offset=0,size=0):
        task = self.get(data, offset=offset, size=size).\
            to_json(ensure_ascii=False)
        return task

    def get_count(self,data):
        return self.get_count(data)

    def save_task(self,data):
        return self.add(data)
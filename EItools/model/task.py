from EItools.common.db_base import DBBase
from EItools.common.connection import *


class Task(Document):
    meta = {
        'collection': 'task',
        'strict': False
    }
    _id = ObjectIdField()
    task_name = StringField()
    creator = StringField()
    creator_id = StringField()
    publish_time = StringField()
    file_name = StringField()
    status = IntField()
    total = IntField()
    has_finished = IntField()


class TaskOpt(DBBase):
    def __init__(self):
        super(TaskOpt, self).__init__(Task)

    def get_task(self, data, offset=0, size=0):
        tasks = self.get(data, offset=offset, size=size).order_by('-publish_time'). \
            as_pymongo()
        tasks_final = []
        for task in tasks:
            task['id'] = str(task['_id'])
            del task['_id']
            tasks_final.append(task)
        return tasks_final

    def get_task_count(self, data):
        return self.get_count(data)

    def save_task(self, data):
        return self.add(data)

    def update_task(self, data, update_data):
        self.update(self.get(data), update_data)

    def filter_task(self, data, fields=None):
        tasks = self.object_filter(data).fields(**fields).as_pymongo()
        tasks_new = []
        for task in tasks:
            task['id'] = str(task['_id'])
            del task['_id']
            tasks_new.append(task)
        return tasks_new

from EItools.common.db_base import DBBase
from EItools.common.connection import *


class uncrawled_person(Document):
    meta = {
        'collection': 'uncrawled_person',
        'strict': False
    }
    _id = ObjectIdField()
    name = StringField()
    org = StringField()
    task_id = ObjectIdField()
    status = IntField()


class UncrawledPersonOpt(DBBase):
    def __init__(self):
        super(UncrawledPersonOpt, self).__init__(uncrawled_person)

    def get_uncrawled_person(self, data, offset=0, size=0):
        uncrawled_persons = self.get(data, offset=offset, size=size). \
            as_pymongo()
        persons = []
        for person in uncrawled_persons:
            person['id'] = str(person['_id'])
            del person['_id']
            person['task_id'] = str(person['task_id'])
            persons.append(person)
        return persons

    def get_uncrawled_person_count(self, data):
        return self.get_count(data)

    def save_uncrawled_person(self, data):
        return self.add(data)

    def update_uncrawled_person(self, data, update_data):
        self.update(self.get(data), update_data)

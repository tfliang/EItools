from mongoengine import StringField, Document, IntField

from EItools.common.db_base import DBBase


class uncrawled_person(Document):
    name=StringField()
    org=StringField()
    task_id=StringField()
    status=IntField()

class UncrawledPersonOpt(DBBase):
    def __init__(self):
        super(UncrawledPersonOpt,self).__init__(uncrawled_person)

    def get_uncrawled_person(self,data,offset=0,size=0):
        uncrawled_persons = self.get(data, offset=offset, size=size).\
            to_json(ensure_ascii=False)
        persons = []
        for person in uncrawled_persons:
            person['id'] = person['_id']['$oid']
            del person['_id']
            persons.append(person)
        return uncrawled_person

    def get_uncrawled_person_count(self,data):
        return self.get_count(data)

    def save_uncrawled_person(self,data):
        return self.add(data)

    def update_uncrawled_person(self,data,update_data):
        self.update(self.get(data),update_data)


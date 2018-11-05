from EItools.common.operation import Operation
from mongoengine.queryset.visitor import Q


class DBBase(object):
    def __init__(self, model):
        self.model = model

    def add(self, data):
        if isinstance(data, dict):
            Operation.add(self.model, **data)

    def update(self, query, data):
        return Operation.update(query, **data)

    def get(self,data,offset=0,size=0):
        return Operation.filter(self.model,offset,size,**data)

    def object_filter_or(self, key1, value1, key2, value2):
        """高级查询 key1 key2 字段为字符串"""
        # query = Model.objects.filter(Q(age=10) | Q(grade=80))
        a = {key1: value1}
        b = {key2: value2}
        c = Q(**a) | Q(**b)
        query = self.model.objects.filter(c)
        return query

    def get_between(self, key, left, right):
        """key 必须为字段字符串"""
        data = dict()
        data[key + "__gt"] = left
        data[key + "__lt"] = right
        return self.get(data)

    def get_great_than(self, key, value):
        """key 必须为字段字符串"""
        data = dict()
        data[key + "__gt"] = value
        return self.get(data)

    def get_less_than(self, key, value):
        """key 必须为字段字符串"""
        data = dict()
        data[key + "__glt"] = value
        return self.get(data)

    def get_in(self, key, values):
        data = dict()
        data[key + "__in"] = values
        return self.get(data)

    def get_require_fields(self, query, data):
        query = Operation.query_fields(query, **data)
        return query

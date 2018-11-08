from mongoengine.queryset.visitor import Q


class DBBase(object):
    def __init__(self, model):
        self.model = model

    def add(self, data):
        if isinstance(data, dict):
            print(data)
            model = self.model(**data)
            model.save()

    def update(self, query, data):
        return query.update(**data)

    def get(self,data,offset=0,size=0):
        if size > 0 and offset >= 0:
            query = self.model.objects(**data).skip(offset).limit(size)
        else:
            query=self.model.objects(**data)
        return query

    def object_filter(self, data,offset=0,size=0):
        """高级查询 key1 key2 字段为字符串"""
        # query = Model.objects.filter(Q(age=10) | Q(grade=80))
        if size > 0 and offset >= 0:
            query = self.model.objects.filter(data).skip(offset).limit(size)
        else:
            query = self.model.objects.filter(data)
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
        query = query.fields(**data)
        return query

    def get_count(self,data):
        return self.model.objects(**data).count()


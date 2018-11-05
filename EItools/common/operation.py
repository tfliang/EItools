from mongoengine.queryset.visitor import Q
class Operation(object):
    @staticmethod
    def add(model, **document_dict):
        model = model(**document_dict)
        model.save()

    @staticmethod
    def get_query(model):
        query = model.objects()
        return query

    @staticmethod
    def delete(query):
        query.delete()

    @staticmethod
    def update(query, **data):
        query.update(**data)

    @staticmethod
    def filter(model,offset=0,size=0,**data):
        if size > 0 and offset >= 0:
            query = model.objects(**data).skip(offset).limit(size)
        else:
            query=model.objects(**data)
        return query

    @staticmethod
    def object_filter(model, **data):
        """高级查询"""
        query = model.objects.filter(**data)
        return query

    @staticmethod
    def query_fields(query, **data):
        """高级查询"""
        query = query.fields(**data)
        return query
if __name__ == '__main__':
    pass
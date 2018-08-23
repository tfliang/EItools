# coding:utf-8
import json
import sys

from io import StringIO
from django.http import HttpResponse

sys.path.append("..")
from EItools.log.log import logger
from EItools.client.mongo_client import MongoDBClient
task_status_dict={
    "finished":0,
    "failed":1,
    "doing":2,
    "not_started":3
}
mongo_client=MongoDBClient()
def get_all_tasks(request):
    logger.info("get all task")
    tasks=mongo_client.get_all_task()
    return HttpResponse(json.dumps(tasks), content_type="application/json")


def export_data(request,taskid):
    task=mongo_client.get_task_by_Id(taskid)
    if task is not None:
        persons=mongo_client.get_crawled_person_by_pid(taskid)
        logger.info(len(persons))
        return write_json(persons,task['file_name'])
    else:
        return HttpResponse(json.dumps({"message":"task error"}), content_type="application/json")

def write_json(data,file_name):
    try:
        json_stream=get_json_stream(data)
        response=HttpResponse(content_type='application/json')
        from urllib import parse
        response['Content-Disposition']='attachment;filename='+parse.quote(file_name)+'.json'
        response.write(json_stream)
        return response
    except Exception as e:
        print(e)

def get_json_stream(data):
    file= StringIO()
    data=json.dumps(data,ensure_ascii=False)
    file.write(data)
    res=file.getvalue()
    file.close()
    return res
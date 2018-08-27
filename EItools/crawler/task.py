# coding:utf-8
import json
import os
import sys

from io import StringIO

from bson import ObjectId
from django.http import HttpResponse

from EItools import settings

sys.path.append("..")
from EItools.log.log import logger
from EItools.client.mongo_client import MongoDBClient
from EItools.crawler.crawl_information import save_task
task_status_dict={
    "finished":0,
    "failed":1,
    "doing":2,
    "not_started":3
}
mongo_client=MongoDBClient()
def get_tasks_by_page(request,offset,size):
    tasks=mongo_client.get_all_task(int(offset),int(size))
    result={
        'total':mongo_client.get_task_count(),
        'offset':offset,
        'size':size,
        'tasks':tasks
    }
    return HttpResponse(json.dumps(result), content_type="application/json")

def get_task_by_id(request,id):
    task=mongo_client.get_task_by_Id(id)
    if task is None:
        result={
           'info':"task not exsits"
        }
    else:
        result=task
    return HttpResponse(json.dumps(result), content_type="application/json")

def publish_task(request):
    if request.method=='POST':
        file_name=request.POST.get('file_name',"")
        task_name=request.POST.get('task_name',"")
        creator_id=request.POST.get('creator_id',"")
        creator=request.POST.get('creator',"")
        task_id=ObjectId()
        file_path = os.path.join(settings.BASE_DIR, 'media/file/%s').replace("\\", "/") % (file_name)
        save_task.apply_async(args=[str(task_id),file_path,task_name,creator,creator_id])
        result={
            'info':"upload success",
            'task_id':task_id
        }
    else:
        result={
            'info':"upload data error"
        }
    return HttpResponse(json.dumps(result), content_type="application/json")


def export_data(request,taskid):
    task=mongo_client.get_task_by_Id(taskid)
    if task is not None:
        persons=mongo_client.get_crawled_person_by_taskId(taskid)
        logger.info(len(persons))
        return write_json(persons,task['task_name'])
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
        logger.info(e)
        return HttpResponse(json.dumps({"message": "task error"}), content_type="application/json")

def get_json_stream(data):
    file= StringIO()
    data=json.dumps(data,ensure_ascii=False)
    file.write(data)
    res=file.getvalue()
    file.close()
    return res
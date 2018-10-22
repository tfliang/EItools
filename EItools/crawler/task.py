# coding:utf-8
import csv
import json
import os
import sys

from io import StringIO
from time import strftime

from bson import ObjectId
from django.http import HttpResponse

from EItools import settings

sys.path.append("..")
from EItools.log.log import logger
from EItools.client.mongo_client import MongoDBClient
from EItools import celery_app
from urllib import parse
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


@celery_app.task
def save_task(task_id,file_path,task_name,creator,creator_id):
    total = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):#row[0] is person name row[1] is org name
                total += 1
                person = dict()
                person['row_number']=i
                person['name'] = row[0]
                person['org'] = row[1]
                person['task_id'] = ObjectId(task_id)
                mongo_client.save_person(person)
        logger.info("pulish task: {} total: {}".format(task_id, total))
        task = dict()
        task['_id'] = ObjectId(str(task_id))
        task['task_name']=task_name
        task['creator']=creator
        task['creator_id']=creator_id
        task['publish_time'] = strftime("%Y-%m-%d %H:%M")
        task['file_name'] = "%s"%(file_path.split("/")[-1])
        task['status'] = task_status_dict['not_started']
        task['total']=total
        mongo_client.save_task(task)
    except Exception as e:
        logger.error("when publish crawl person task : {}".format(e))


def publish_task(request):
    def get_value(key,content):
        return content[key] if key in content else ""
    if request.method=='POST':
        content=json.loads(request.body)
        file_name=get_value('file_name',content)
        task_name=get_value('task_name',content)
        creator_id=get_value('creator_id',content)
        creator=get_value('creator',content)
        task_id=ObjectId()
        file_path = settings.FILE_PATH.replace("\\", "/") % (file_name)
        total = 0
        try:
            save_task.apply_async(args=[str(task_id),file_path,task_name,creator,creator_id])
            result = {
                'info': "upload success",
                'task_id': str(task_id)
            }
        except Exception as e:
            logger.error("when save task: {}".format(e))
            result = {
                'info': "upload data error"
            }

    return HttpResponse(json.dumps(result), content_type="application/json")


def export_data(request,taskid):
    task=mongo_client.get_task_by_Id(taskid)
    if task is not None:
        persons=mongo_client.get_crawled_person_by_taskId(taskid)
        persons_filter=[]
        for person in persons:
            if 'result' in person:
                del person['result']
            if 'info' in person:
                del person['info']
            if 'edu_exp_region' in person:
                del person['edu_exp_region']
            if 'exp_region' in person:
                del person['exp_region']
            if 'academic_org_exp_region' in person:
                del person['academic_org_exp_region']
            if 'awards_region' in person:
                del person['awards_region']
            if 'patents_region' in person:
                del person['patents_region']
            if 'projects_region' in person:
                del person['projects_region']
            if 'citation' in person:
                del person['citation']
            if 'source' in person:
                del person['source']
            if 'status' in person:
                del person['status']
            persons_filter.append(person)
        logger.info("export {} total {} person".format(taskid,len(persons)))
        return write_json(persons,task['task_name'])
    else:
        return HttpResponse(json.dumps({"message":"task error"}), content_type="application/json")

def write_json(data,file_name):
    try:
        json_stream=get_json_stream(data)
        response=HttpResponse(content_type='application/json')
        response['Content-Disposition']='attachment;filename='+parse.quote(file_name)+'.json'
        response.write(json_stream)
        return response
    except Exception as e:
        logger.error("save upload file:{}".format(e))
        return HttpResponse(json.dumps({"message": "task error"}), content_type="application/json")

def get_json_stream(data):
    file= StringIO()
    data=json.dumps(data,ensure_ascii=False)
    file.write(data)
    res=file.getvalue()
    file.close()
    return res
# coding:utf-8
import os
import re
import sys

from mongoengine import Q

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from EItools.model.crawled_person import CrawledPersonOpt
from EItools.model.task import TaskOpt
from EItools.model.uncrawled_person import UncrawledPersonOpt
import time
from EItools.crawler import crawl_service
import json
from django.http import HttpResponse
from EItools.log.log import logger
from EItools import celery_app, settings


task_status_dict={
    "finished":0,
    "failed":1,
    "doing":2,
    "not_started":3
}
person_status_dict={
    "finished": 0,
    "failed": 1,
}

def get_value(key, content):
    return content[key] if key in content else ""

def crawl_file_info(request):
    logger.info("save file start")
    csv_file = request.FILES['file']
    file_name="%f-%s"%(int(time.time()),csv_file.name)
    file_path = settings.FILE_PATH.replace("\\", "/") % (file_name)
    with open(file_path, 'wb+') as f:
        for i, chunk in enumerate(csv_file.chunks()):
            f.write(chunk)
    logger.info("save file end")
    return HttpResponse(json.dumps({"file_name": file_name}), content_type="application/json")


def crawl_person_by_name(request):
    name=request.GET.get('name','')
    org=request.GET.get('org','')
    persons=[]
    persons_info={}
    if name !="" and org !="":
        person={
            'name':name,
            'org':org
        }
        persons.append(person)
        persons_info=crawl_service.crawl_person_info(persons,None,from_api=True)
    return HttpResponse(json.dumps({"info": persons_info}), content_type="application/json")

def crawl_person_by_id(request,id):
    person=CrawledPersonOpt().get_crawled_person({'_id':id})
    if person is not None:
        persons_info=crawl_service.crawl_person_info([person],None)
        return HttpResponse(json.dumps({"info": persons_info}), content_type="application/json")
    return HttpResponse(json.dumps({"info": "person not exists"}), content_type="application/json")


def update_person_by_field(request):
    person_id = request.GET.get('person_id', '')
    field_key = request.GET.get('field_key', '')
    field_value=request.GET.get('field_value','')
    if person_id=="" or field_key == "" or field_value == "":
        info="info not exists"
    else:
        CrawledPersonOpt().update({"_id":person_id},{"$set": {field_key: field_value}})
        info="info update success"
    return HttpResponse(json.dumps({"info": info}), content_type="application/json")


def get_crawled_persons_by_taskId(request,id,offset,size):
    crawled_persons=CrawledPersonOpt().get_crawled_person({'task_id':id},offset=int(offset),size=int(size),part='list')
    result = {
        'total': CrawledPersonOpt().get_count({'task_id':id}),
        'offset': offset,
        'size': size,
        'info': crawled_persons
    }
    return HttpResponse(json.dumps(result), content_type="application/json")

def search_crawled_persons(request):
    if request.method=='POST':
        content=json.loads(request.body)
        person_name=get_value('search_value',content)
        task_id=get_value('task_id',content)
        offset=get_value('offset',content)
        size=get_value('size',content)
        crawled_persons=CrawledPersonOpt().get_crawled_person({'task_id': task_id,"name":re.compile(person_name)}, offset=int(offset), size=int(size), part='list')
        result = {
            'total': CrawledPersonOpt().get_count({'task_id': task_id,"name":re.compile(person_name)}),
            'offset': offset,
            'size': size,
            'info': crawled_persons
        }
    else:
        result = {
            'info': "error search"
        }

    return HttpResponse(json.dumps(result), content_type="application/json")

def get_crawled_persons_by_personId(request,id):
    person=CrawledPersonOpt().get_crawled_person({'_id':id},part="one")

    if len(person)>0:
        return HttpResponse(json.dumps(person[0]), content_type="application/json")

    return HttpResponse({}, content_type="application/json")


def update_person_by_Id(request):
    if request.method == 'POST':
        person = json.loads(request.body)
        person_id = get_value('id', person)
        del person['id']
        if CrawledPersonOpt().get_count({'_id':person_id})>0:
            for key,value in person.items():
               CrawledPersonOpt().update(CrawledPersonOpt().get({'_id':person_id}),{key:value})
            return HttpResponse(json.dumps({"info": "save success"}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"info": "id not exists"}), content_type="application/json")

def view_person_changeinfo(request,id):
    crawled_person_changeinfo_list=CrawledPersonOpt().filter_person({"changed":True,"_id":id})
    return HttpResponse(json.dumps(crawled_person_changeinfo_list), content_type="application/json")

def view_person_changeinfo_list(request,offset,size):
    crawled_persons_changeinfo_list = CrawledPersonOpt().filter_person({"changed":True},offset=int(offset),size=int(size))
    result = {
        'total': CrawledPersonOpt().get_count({"changed":True}),
        'offset': offset,
        'size': size,
        'info': crawled_persons_changeinfo_list
    }
    return HttpResponse(json.dumps(result), content_type="application/json")

def search_person_changeinfo_list(request):
    if request.method == 'POST':
        content = json.loads(request.body)
        person_name = get_value('search_value', content)
        offset = get_value('offset', content)
        size = get_value('size', content)
        crawled_persons = CrawledPersonOpt().filter_person({"changed": True,"name":re.compile(person_name)}, offset=int(offset), size=int(size))
        result = {
            'total': CrawledPersonOpt().get_count({"changed": True,"name":re.compile(person_name)}),
            'offset': offset,
            'size': size,
            'info': crawled_persons
        }
    else:
        result = {
            'info': "error search"
        }

    return HttpResponse(json.dumps(result), content_type="application/json")




def crawl_google_scholar(request):
    if request.method == 'POST':
        person={}
        person['name']="李涓子"
        person['org']="清华"
        crawl_service.crawl_google_scholar(person)


@celery_app.task
def publish_task():
    for task in TaskOpt().filter_task(Q(status=task_status_dict['failed'])|Q(status=task_status_dict['not_started']),{"_id":1}):
        total = UncrawledPersonOpt().get_count({"task_id":task['id']})
        if total>0:
            persons = UncrawledPersonOpt().get_uncrawled_person({'task_id':task['id']})
            TaskOpt().update_task({'_id':task['id']},{'status':task_status_dict['doing']})
            logger.info("not finished is {},this task has {} person".format(task['id'], len(persons)))
            size = 1
            offset = 0
            if len(persons) > 0:
                try:
                    while (offset < len(persons)):
                        crawl_service.crawl_person_info.apply_async(args=[persons[offset:offset + size], task['id']])
                        offset += size
                except Exception as e:
                    logger.error("crawl info task exception: %s", e)



@celery_app.task
def clean_task():
    for id in TaskOpt().get_task({"status": task_status_dict['doing']}):
        total = UncrawledPersonOpt().get_count({"task_id":id})
        if total==0:
            TaskOpt().update({'_id':id},{'status':task_status_dict['finished']})






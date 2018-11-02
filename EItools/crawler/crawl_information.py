# coding:utf-8
import multiprocessing
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from EItools.client.mongo_client import mongo_client
import time
from EItools.crawler import crawl_service
import json
from django.http import HttpResponse
from bson import ObjectId
from EItools.log.log import logger
from EItools import celery_app, settings


task_status_dict={
    "finished":0,
    "failed":1,
    "doing":2,
    "not_started":3
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

@celery_app.task
def start_crawl(id):
    persons = mongo_client.get_uncrawled_person_by_taskId(id)
    logger.info("not finished is {},this task has {} person".format(id,len(persons)))
    size=1
    offset=0
    if len(persons) > 0:
        try:
            while(offset<len(persons)):
                crawl_service.crawl_person_info.apply_async(args=[persons[offset:offset+size],id])
                offset+=size
        except Exception as e:
            logger.error("crawl info task exception: %s",e)
            #mongo_client.update_task(task_status_dict['failed'], id)
    #mongo_client.update_task(task_status_dict['finished'], id)
    #logger.info("task exit" + id)

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
        persons_info=crawl_service.crawl_person_info(persons,None)
    return HttpResponse(json.dumps({"info": persons_info}), content_type="application/json")

def crawl_person_by_id(request,id):
    person=mongo_client.get_crawled_person_by_pid(id)
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
        mongo_client.update_person_by_keyvalue(person_id,field_key,field_value)
        info="info update success"
    return HttpResponse(json.dumps({"info": info}), content_type="application/json")


def get_crawled_persons_by_taskId(request,id,offset,size):
    crawled_persons=mongo_client.get_crawled_person_by_taskId(id,int(offset),int(size))
    #uncrawled_persons=mongo_client.get_uncrawled_person_by_taskId(id)
    total_persons=[]
    crawled_persons_final=[]
    for person in crawled_persons:
        if 'result' in person:
            del person['result']
        if 'info' in person:
            del person['info']
        if 'email' in person and person['email']==[] and len(person['emails_prob'])>0:
            person['email']=person['emails_prob'][0][0]
        total_persons.append(person)
        #crawled_persons_final.append(person)
    # for person in uncrawled_persons:
    #     person['status']=0
    #     total_persons.append(person)
    result = {
        'total': mongo_client.get_crawled_person_num_by_taskId(id),
        'offset': offset,
        'size': size,
        'info': total_persons
    }
    return HttpResponse(json.dumps(result), content_type="application/json")

def search_crawled_persons(request):
    if request.method=='POST':
        content=json.loads(request.body)
        person_name=get_value('search_value',content)
        task_id=get_value('task_id',content)
        offset=get_value('offset',content)
        size=get_value('size',content)
        crawled_persons = mongo_client.search_crawled_person_by_taskId(task_id, person_name,int(offset), int(size))
        # uncrawled_persons=mongo_client.get_uncrawled_person_by_taskId(id)
        total_persons = []
        crawled_persons_final = []
        for person in crawled_persons:
            if 'result' in person:
                del person['result']
            if 'info' in person:
                del person['info']
            if 'email' in person and person['email'] == [] and len(person['emails_prob']) > 0:
                person['email'] = person['emails_prob'][0][0]
            person['status'] = 1
            total_persons.append(person)
            # crawled_persons_final.append(person)
        # for person in uncrawled_persons:
        #     person['status']=0
        #     total_persons.append(person)
        result = {
            'total': mongo_client.search_crawled_person_num_by_taskId(task_id,person_name),
            'offset': offset,
            'size': size,
            'info': total_persons
        }
    else:
        result = {
            'info': "error search"
        }

    return HttpResponse(json.dumps(result), content_type="application/json")

def get_crawled_persons_by_personId(request,id):
    person=mongo_client.get_crawled_person_by_pid(id)
    if person is not None:
        person['id'] = str(person['_id'])
        del person['_id']
        del person['task_id']
        if 'result' in person:
            del person['result']
        if 'info' in person:
            del person['info']
        if 'email' in person and person['email']==[] and len(person['emails_prob'])>0:
            person['email']=person['emails_prob'][0][0]
        person['status']=1
        return HttpResponse(json.dumps(person), content_type="application/json")
    return HttpResponse({}, content_type="application/json")


def update_person_by_Id(request):
    if request.method == 'POST':
        person = json.loads(request.body)
        person_id = get_value('id', person)
        del person['id']
        if mongo_client.get_crawled_person_by_pid(person_id) is not None:
            for key,value in person.items():
                mongo_client.update_crawled_person_by_keyvalue(person_id,key,value)
            return HttpResponse(json.dumps({"info": "save success"}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"info": "id not exists"}), content_type="application/json")

def update_person_by_detail(request):
    if request.method == 'POST':
        person = json.loads(request.body)
        person_id = get_value('id', person)
        if mongo_client.get_crawled_person_by_pid(person_id) is not None:
            person['_id']=ObjectId(person_id)
            del person['id']
            mongo_client.save_person(person)
            return HttpResponse(json.dumps({"info": "save success"}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"info": "id not exists"}), content_type="application/json")

def view_person_changeinfo(request):
    crawled_person_changeinfo_list=mongo_client.get_changeinfo_list()
    return HttpResponse(json.dumps(crawled_person_changeinfo_list), content_type="application/json")

def view_person_changeinfo_list(request):
    if request.method=='POST':
        content=json.loads(request.body)
        offset = get_value('offset', content)
        size = get_value('size', content)
        crawled_persons_changeinfo_list = mongo_client.get_changeinfo_list()
        result = {
            'total': mongo_client.get_changeinfo_num(),
            'offset': offset,
            'size': size,
            'info': crawled_persons_changeinfo_list
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
    for id in mongo_client.get_unfinished_task():
        logger.info("not finished task {}".format(id))
        total = mongo_client.get_person_num_by_taskId(id)
        logger.info("total:{}".format(total))
        if total>0:
            start_crawl.apply_async(args=[str(id)])



@celery_app.task
def clean_task():
    for id in mongo_client.get_doing_task():
        total = mongo_client.get_person_num_by_taskId(id)
        if total==0:
            mongo_client.update_task(task_status_dict['finished'],id)






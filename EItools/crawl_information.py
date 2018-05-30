#coding:utf-8
import csv
import os
import sys
sys.path.append("..")
import re
from time import strftime
from bson import ObjectId
from django.shortcuts import render
from EItools.log.log import logger
from EItools import settings
from EItools.client.rest_client import RESTClient
from EItools.model.file_forms import BatchOptForm

from EItools.src.crawler import PhoneCrawler
from EItools.src import pre_process
from EItools import celery_app
from EItools.client.mongo_client import MongoDBClient

#class GracefulKiller:
    #kill_now=False

    #def __init__(self):
        #signal.signal(signal.SIGINT,self.exit_gracefully)
        #signal.signal(signal.SIGTERM,self.exit_gracefully)

    #def exit_gracefully(self,signum,frame):
        #logger.info('program will exit')
        #self.phonecrawler.kill_crawlers()
mongo_client = MongoDBClient()
def crawl_file_info(request):
    logger.info("crawl file info start")
    batch_form = BatchOptForm(request.POST, request.FILES)
    csv_file=request.FILES['file']
    file_path=os.path.join(settings.BASE_DIR,'media/file/%s').replace("\\","/")%(csv_file.name)
    with open(file_path,'wb+') as f:
        for chunk in csv_file.chunks():
            print(str(chunk))
            f.write(chunk)
    with open(file_path,'r',encoding='utf-8') as f:
        reader=csv.reader(f)
        task_id= ObjectId()
        for i,row in enumerate(reader):
            person=dict()
            person['name']=row[0]
            person['org']=row[1]
            person['taskId']=task_id
            mongo_client.save_person(person)
        task=dict()
        task['_id']=task_id
        task['publish_time']=strftime("%m/%d/%Y %H:%M")
        task['file_name']=csv_file.name
        mongo_client.save_task(task)
        start_crawl.apply_async(args=[task_id.__str__(),])
    return render(request, "upload_file.html")

def crawl_DB_info(request):
    logger.info("crawl db info start")
    persons=mongo_client.get_test_person_info(30000,2000)
    taskId = ObjectId()
    for i,p in enumerate(persons):
        person=dict()
        person['name']=p['name']
        person['org']=p['单位' ]
        person['taskId']=taskId
        mongo_client.save_person(person)
    task=dict()
    task['_id'] = taskId
    task['publish_time'] = strftime("%m/%d/%Y %H:%M")
    mongo_client.save_task(task)
    start_crawl.apply_async(args=[taskId.__str__(), ])
    logger.info("crawl db request end")
    return render(request, "upload_file.html")

@celery_app.task
def start_crawl(id):
    #killer = GracefulKiller()
    logger.info(id)
    persons = mongo_client.get_person_by_taskId(id)
    logger.info(len(persons))
    crawInfo = mongo_client.get_crawl_info()
    phoneCrawler = PhoneCrawler()
    phoneCrawler.load_crawlers()
    for i,p in enumerate(persons):
        person=dict()
        person['name']=p['name']
        affs=pre_process.get_valid_aff(p['org'])
        person['simple_affiliation']=affs
        info,url=phoneCrawler.get_info(person)
        p['s_aff']=affs
        p['url']=url
        p['info']=info
        crawInfo.save(p)
    mongo_client.update_task("1",id)
    # if not killer.kill_now:
    #     phoneCrawler.shutdown_crawlers()
    logger.info("program exit")
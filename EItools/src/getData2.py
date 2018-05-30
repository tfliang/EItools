#coding:utf-8
import sys
from celery import Celery

from EItools.log.log import logger
from EItools.src import pre_process

sys.path.append("..")
import re
from time import strftime
from bson import ObjectId
from EItools.client.rest_client import RESTClient
from EItools.src.crawler import PhoneCrawler
from EItools.client.mongo_client import MongoDBClient
from EItools.utils import chinese_helper
#class GracefulKiller:
    #kill_now=False

    #def __init__(self):
        #signal.signal(signal.SIGINT,self.exit_gracefully)
        #signal.signal(signal.SIGTERM,self.exit_gracefully)

    #def exit_gracefully(self,signum,frame):
        #logger.info('program will exit')
        #self.phonecrawler.kill_crawlers()

def crawlInfo():
    logger.info("program start")
    mongoClient = MongoDBClient()
    persons = mongoClient.get_test_person()
    taskId=ObjectId()
    for i,p in enumerate(persons):
        print(i)
        logger.info(i)
        if i>20000:
            if i%2000==0:
                logger.info(i)
                startCrawl(taskId.__str__())
                taskId = ObjectId()
                task = dict()
                task['_id'] = taskId
                task['publish_time'] = strftime("%m/%d/%Y %H:%M")
                task['file_name'] = "张三"
                mongoClient.save_task(task)
            person=dict()
            person['name']=p['name']
            person['org']=p['单位']
            person['taskId']=taskId
            mongoClient.save_person(person)


def startCrawl(id):
    #killer = GracefulKiller()
    mongoClient = MongoDBClient()
    restClient = RESTClient()
    logger.info(id)
    persons = mongoClient.get_person_by_taskId(id)
    logger.info(len(persons))
    crawInfo = mongoClient.get_crawl_info()
    phoneCrawler = PhoneCrawler()
    phoneCrawler.load_crawlers()
    for i,p in enumerate(persons):
        person=dict()
        person['name']=p['name']
        affs = pre_process.get_valid_aff(p['org'])
        person['simple_affiliation']=affs
        info,url=phoneCrawler.get_info(person)
        p['s_aff']=affs
        p['url']=url
        p['info']=info
        crawInfo.save(p)
    mongoClient.update_task("1",id)
    # if not killer.kill_now:
    #     phoneCrawler.shutdown_crawlers()
    logger.info("task {} finished".format(id))

crawlInfo()
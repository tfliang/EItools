# coding:utf-8
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import csv
import json
import os
import requests
from django.http import HttpResponse
import time
from time import strftime
from bson import ObjectId
from EItools.log.log import logger
from EItools import settings
from EItools.utils import chinese_helper
from EItools.chrome.crawler import InfoCrawler
from EItools.chrome import pre_process
from EItools import celery_app
from EItools.client.mongo_client import MongoDBClient
from EItools.extract.interface import interface
task_status_dict={
    "finished":0,
    "failed":1,
    "doing":2,
    "not_started":3
}
def crawl_file_info(request):
    logger.info("crawl file info start")
    csv_file = request.FILES['file']
    file_name="%f-%s"%(int(time.time()),csv_file.name)
    file_path = os.path.join(settings.BASE_DIR, 'media/file/%s').replace("\\", "/") % (file_name)
    with open(file_path, 'wb+') as f:
        for i, chunk in enumerate(csv_file.chunks()):
            f.write(chunk)
    logger.info("crawl file info end")
    return HttpResponse(json.dumps({"file_name": file_name}), content_type="application/json")


@celery_app.task
def save_task(file_path,task_name,creator,creator_id):
    mongo_client = MongoDBClient()
    task_id = ObjectId()
    size=1000
    k = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):#row[0] is person name row[1] is org name
                k += 1
                person = dict()
                person['name'] = row[0]
                person['org'] = row[1]
                person['taskId'] = task_id
                mongo_client.db['uncrawled_person'].save(person)
        logger.info("pulish task: {} total: {}".format(task_id, k))
        task = dict()
        task['_id'] = task_id
        task['task_name']=task_name
        task['creator']=creator
        task['creator_id']=creator_id
        task['publish_time'] = strftime("%Y-%m-%d %H:%M")
        task['file_name'] = "%s"%(file_path.split("/")[-1])
        task['status'] = task_status_dict['not_started']
        task['total']=k
        mongo_client.save_task(task)
    except Exception as e:
        logger.info(e)


def get_data_from_aminer(person):
    post_json = {
        "action": "search.search", "parameters": {"advquery": {
            "texts": [{"source": "name", "text": ""}, {"source": "org", "text": ""}]},
            "offset": 0, "size": 10, "searchType": "SimilarPerson"},
        "schema": {
            "person": ["id", "name", "name_zh", "profile.affiliation", "avatar", "profile.affiliation_zh",
                       "profile.position", "profile.position_zh", {"indices": ["hindex", "pubs", "citations"]}]}
    }
    url = "https://apiv2.aminer.cn/magic"
    headers = {
        'Content-Type':"application/json",
        'Debug':"1",
        'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyLSt0ZTl2SHRVSGIycWhBM2ZlMVM4MGQrWWFIVlhCUkZjT1BHZTZhVDlmRytZZktadEs2dDNOSDdJSk5NZUtBa3NZXC9tSTFmcE1rTWJZQ0toZHlQN1lkQ2UwNjQyemhzK0xCdVBFRkVXRSIsInVpZCI6IjU2YTA0MmJlYzM1ZjRmNjVmNzdmNzhkYiIsInNyYyI6ImFtaW5lciIsInJvbGVzIjpbInJvc3Rlcl9lZGl0b3IiXSwiaXNzIjoiYXBpLmFtaW5lci5vcmciLCJleHAiOjE1MzIwNTE1OTEsImlhdCI6MTUyOTQ1OTU5MSwianRpIjoiMDMzMDdmMjM5MjQzZDhhNjQzMmZlOWMxOGVlNGQ4M2E5NDdhYzQwMzJmNzA1ODlkNWI0YzNkOWU0NjMwNThmNDgzNDAyZmE3ODFjMGNiNWJkY2QxMjMwM2MwZjUzOTZlNmRjZjA2ZmRhZWZkMjMzYTkwZmZlYzczYzA4NGI3M2Q0MTFhZmQyZGM3NGM2NjJjNTU2YTdkZGRlZjM5ZmFmMWUxZmRhYjQ4YTg0YmU0MWY5YTMxOWJkMjFhYWU4ZWUwZGVhNWU2ZDhkOGNiNGFmMjcxMmY4ZWQ4ZmE0MzExODJhN2I4NjVkNWE1NDVkMDVjOTY0OTI0YzkzNDExYzk0MCIsImVtYWlsIjoiMjcxODU4Mzc0MUBxcS5jb20ifQ.tU-8icEsCvR_88RNFdpVrk-xNBk3_Ovxtq-wegmzo28'}
    try:
        post_json['parameters']['advquery']['texts'][0]['text'] = person['name']
        post_json['parameters']['advquery']['texts'][1]['text'] = person['simple_affiliation']
        resp = requests.post(url, headers=headers, json=[post_json])
        ok, result = get_resp_result(resp)
        print(ok)
        if ok and 'items' in result["data"][0]:
            sleepTime = 0  # have data, don't sleep
            for candidate in result["data"][0]["items"]:
                if 'profile' in candidate and 'affiliation' in candidate['profile']:
                    simple_affiliation = candidate['profile']['affiliation']
                elif 'profile' in candidate and 'org' in candidate['profile']:
                    simple_affiliation = candidate['profile']['org']
                else:
                    simple_affiliation = ''
                if 'name' in candidate:
                    person_name = candidate['name']
                    sim_name = chinese_helper.simila_name(person_name, person['name'])
                    sim_aff = chinese_helper.simila_name(simple_affiliation, ''.join(person['simple_affiliation']))
                    if sim_name > 0 and sim_aff > 0:
                        return True, candidate
    except Exception as e:
        print(e)
        logger.error("%s, %s", "request url error", e)
    return False, person

def save_data_to_expertbase(person):
    post_json = {

    }
    url = "https://apiv2.aminer.cn/magic"
    headers = {
        'Content-Type': "application/json",
        'Debug': "1",
        'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyLSt0ZTl2SHRVSGIycWhBM2ZlMVM4MGQrWWFIVlhCUkZjT1BHZTZhVDlmRytZZktadEs2dDNOSDdJSk5NZUtBa3NZXC9tSTFmcE1rTWJZQ0toZHlQN1lkQ2UwNjQyemhzK0xCdVBFRkVXRSIsInVpZCI6IjU2YTA0MmJlYzM1ZjRmNjVmNzdmNzhkYiIsInNyYyI6ImFtaW5lciIsInJvbGVzIjpbInJvc3Rlcl9lZGl0b3IiXSwiaXNzIjoiYXBpLmFtaW5lci5vcmciLCJleHAiOjE1MzIwNTE1OTEsImlhdCI6MTUyOTQ1OTU5MSwianRpIjoiMDMzMDdmMjM5MjQzZDhhNjQzMmZlOWMxOGVlNGQ4M2E5NDdhYzQwMzJmNzA1ODlkNWI0YzNkOWU0NjMwNThmNDgzNDAyZmE3ODFjMGNiNWJkY2QxMjMwM2MwZjUzOTZlNmRjZjA2ZmRhZWZkMjMzYTkwZmZlYzczYzA4NGI3M2Q0MTFhZmQyZGM3NGM2NjJjNTU2YTdkZGRlZjM5ZmFmMWUxZmRhYjQ4YTg0YmU0MWY5YTMxOWJkMjFhYWU4ZWUwZGVhNWU2ZDhkOGNiNGFmMjcxMmY4ZWQ4ZmE0MzExODJhN2I4NjVkNWE1NDVkMDVjOTY0OTI0YzkzNDExYzk0MCIsImVtYWlsIjoiMjcxODU4Mzc0MUBxcS5jb20ifQ.tU-8icEsCvR_88RNFdpVrk-xNBk3_Ovxtq-wegmzo28'}
    try:
        post_json['parameters']['advquery']['texts'][0]['text'] = person['name']
        post_json['parameters']['advquery']['texts'][1]['text'] = person['simple_affiliation']
        resp = requests.post(url, headers=headers, json=[post_json])
        ok, result = get_resp_result(resp)
        print(ok)
        if ok and 'items' in result["data"][0]:
            return ok
    except Exception as e:
        print(e)
        logger.error("%s, %s", "request url error", e)
    return False

def get_resp_result(resp):
    if resp.status_code == 200:
        result = json.loads(resp.text)
        if result["data"][0]["succeed"]:
            return True, result
    else:
        logger.error("request %s error: %s", resp.url, resp.text)
    return False, None


mongo_client = MongoDBClient()


@celery_app.task
def start_crawl(id,offset,size):
    logger.info("task begin id:{} offset:{} size:{} ".format(id, offset, size))
    persons = mongo_client.get_uncrawled_person_by_taskId(id, offset, size)
    logger.info("this task has {} person".format(len(persons)))
    if len(persons) > 0:
        infoCrawler = InfoCrawler()
        infoCrawler.load_crawlers()
        for i, p in enumerate(persons):
    # persons = mongo_client.crawed_person_col.find()
    # j = 0
    # for i, p in enumerate(persons):
            if 'name' not in p:
                p = mongo_client.person_col.find({"_id": p['_id']})
                if p is not None:
                    j = j + 1
                person = {}
                print(p['name'])
                person['name'] = p['name']
                #affs = pre_process.get_valid_aff(p['org'])
                #person['simple_affiliation'] = ' '.join(affs)
                person['simple_affiliation'] = p['org']
                success,p1=get_data_from_aminer(person)
                if success:
                    p=p1
                    p['source'] = 'aminer'
                    mongo_client.save_crawled_person(p1)
                else:
                    info, url = infoCrawler.get_info(person)
                    emails_prob=infoCrawler.get_emails(person)
                    citation,h_index=infoCrawler.get_scholar_info(person)
                    #if affs is not None:
                        #p['s_aff'] = affs
                    p['url'] = url
                    p['info'] = info
                    p['citation']=citation
                    p['h_index']=h_index
                    #p = extract_information.extract(info, p)
                    #result=interface(info)
                    #PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ=result if result is not None else (None,None,None,None,None,None,None,None,None,None,None,None)
                    # p['aff']=AFF
                    # p['title']=TIT
                    # p['job']=JOB
                    # p['achieve']=DOM
                    # p['awards']=AWD
                    # p['exp']=WRK
                    # p['patents']=PAT
                    # p['projects']=PRJ
                    # p['academic_org_exp']=SOC
                    #p['PER'] = PER
                    #p['ADR'] = ADR
                    #p['AFF'] = AFF
                    #p['TIT'] = TIT
                    #p['JOB'] = JOB
                    #p['DOM'] = DOM
                    #p['EDU'] = EDU
                    #p['WRK'] = WRK
                    #p['SOC'] = SOC
                    #p['AWD'] = AWD
                    #p['PAT'] = PAT
                    #p['PRJ'] = PRJ
                    p['source'] = 'crawler'
                    p['emails_prob']=emails_prob
                    mongo_client.db['crawled_person'].save(p)
                    #存入智库

                #mongo_client.rm_person_by_id(p['_id'])
                mongo_client.update_person_by_id(str(p['_id']))
        infoCrawler.shutdown_crawlers()
    logger.info("task exit" + id)


@celery_app.task
def publish_task():
    for id in mongo_client.get_unfinished_task():
        total = mongo_client.get_person_num_by_taskId(id)
        offset = int(total / 2) + 1
        size=5000
        while offset < total:
            start_crawl.apply_async(args=[str(id), offset,size])
            offset += size


# @celery_app.task
# def do_task(request):
#     offset=0
#     total = mongo_client.get_person_num_by_taskId('5b5f02a4421aa9031208072c')
#     total = int(total / 2)
#     size = int(total / 3) + 1
#     while offset < total:
#         start_crawl.apply_async(args=[str('5b5f02a4421aa9031208072c'), offset, size])
#         offset += size
#     return HttpResponse(json.dumps({"info": "upload success"}), content_type="application/json")


@celery_app.task
def clean_task():
    for id in mongo_client.get_doing_task():
        total = mongo_client.get_person_num_by_taskId(id)
        if total==0:
            mongo_client.update_task(task_status_dict['finished'],id)



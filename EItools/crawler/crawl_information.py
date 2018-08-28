# coding:utf-8
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from EItools.crawler import crawl_mainpage, process
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
from EItools import celery_app
from EItools.client.mongo_client import MongoDBClient
from EItools.extract.interface import interface
from EItools.extract import util

task_status_dict={
    "finished":0,
    "failed":1,
    "doing":2,
    "not_started":3
}
mongo_client = MongoDBClient()

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
def save_task(task_id,file_path,task_name,creator,creator_id):
    task_id = ObjectId(str(task_id))
    print(file_path)
    total = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):#row[0] is person name row[1] is org name
                total += 1
                person = dict()
                person['name'] = row[0]
                person['org'] = row[1]
                person['task_id'] = task_id
                mongo_client.db['uncrawled_person'].save(person)
        logger.info("pulish task: {} total: {}".format(task_id, total))
        task = dict()
        task['_id'] = task_id
        task['task_name']=task_name
        task['creator']=creator
        task['creator_id']=creator_id
        task['publish_time'] = strftime("%Y-%m-%d %H:%M")
        task['file_name'] = "%s"%(file_path.split("/")[-1])
        task['status'] = task_status_dict['not_started']
        task['total']=total
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

@celery_app.task
def start_crawl(id):
    persons = mongo_client.get_uncrawled_person_by_taskId(id)
    logger.info("this task has {} person".format(len(persons)))
    if len(persons) > 0:
        # try:
        crawl_person_info(persons)
        mongo_client.update_task(task_status_dict['finished'], id)
        # except Exception as e:
        #     logger.error("crawl info task exception: %s",e)
        #     mongo_client.update_task(task_status_dict['failed'], id)
    logger.info("task exit" + id)

def crawl_person_by_id(request):
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
        persons_info=crawl_person_info(persons)
    return HttpResponse(json.dumps({"info": persons_info}), content_type="application/json")

def get_crawled_persons_by_taskId(request,id):
    crawled_persons=mongo_client.get_crawled_person_by_taskId(id)
    crawled_persons_final=[]
    for person in crawled_persons:
        del person['result']
        if 'info' in person:
            del person['info']
        if 'email' in person and person['email']==[] and len(person['emails_prob'])>0:
            person['email']=person['emails_prob'][0][0]

        crawled_persons_final.append(person)
    return HttpResponse(json.dumps({"info": crawled_persons_final}), content_type="application/json")


def crawl_person_info(persons):
    infoCrawler = InfoCrawler()
    infoCrawler.load_crawlers()
    persons_info=[]
    for i, p in enumerate(persons):
        if 'name' in p:
            person = {}
            person['name'] = p['name']
            # affs = pre_process.get_valid_aff(p['org'])
            # person['simple_affiliation'] = ' '.join(affs)
            person['simple_affiliation'] = p['org']
            success, p1 = get_data_from_aminer(person)
            if success:
                p = p1
                p['source'] = 'aminer'
                # mongo_client.save_crawled_person(p1)
            else:
                result = process.Get('{},{}'.format(person['name'],person['simple_affiliation']))
                # mongo_client.db['search'].update({"_id": p['_id']}, {"$set": {"result": result}})
                p['result'] = result
                #positive_result=[ r for r in result['res'] if r['label']==1.0]
                result_sorted = sorted(result['res'], key=lambda s: s['score'], reverse=True)
                if len(result_sorted) > 0 :
                    p['url'] = result_sorted[0]['url']
                    p['source'] = 'crawler'
                    p['info'] = crawl_mainpage.get_main_page(p['url'],person)

                # info, url = infoCrawler.get_info(person)
                emails_prob = infoCrawler.get_emails(person)
                citation, h_index ,citation_in_recent_five_year = infoCrawler.get_scholar_info(person)
                # if affs is not None:
                # p['s_aff'] = affs
                # p['url'] = url
                # p['info'] = info
                p['citation'] = citation
                p['h_index'] = h_index
                # p = extract_information.extract(info, p)
                if 'info' in p:
                    result = interface(p['info'])
                    PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ = result if result is not None else (
                    None, None, None, None, None, None, None, None, None, None, None, None)
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
                    # p['AFF'] = AFF
                    # p['TIT'] = TIT
                    # p['JOB'] = JOB
                    # p['DOM'] = DOM
                    # p['EDU'] = EDU
                    # p['WRK'] = WRK
                    # p['SOC'] = SOC
                    # p['AWD'] = AWD
                    # p['PAT'] = PAT
                    # p['PRJ'] = PRJ
                    p['aff']={}
                    p['aff']['inst'] = ' '.join(AFF) if AFF is not None else ""
                    p['title'] = ''.join(TIT) if TIT is not None else ""
                    p['position'] = ''.join(JOB) if JOB is not None else ""
                    p['domain'] = ''.join(DOM) if DOM is not None else ""
                    p['EDU'] = EDU
                    p['exp'] = ''.join(WRK) if WRK is not None else ""
                    p['academic_org_exp'] = ' '.join(SOC) if SOC is not None else ""
                    p['awards'] = ''.join(AWD) if AWD is not None else ""
                    p['patents'] = ''.join(PAT) if PAT is not None else ""
                    p['projects'] = ''.join(PRJ) if PRJ is not None else ""
                    p['gender']=util.find_gender(p['info'])
                    p['email']=util.find_email(p['info'])
                p['source'] = 'crawler'
                p['emails_prob'] = emails_prob
                persons_info.append(p)
                mongo_client.crawed_person_col.save(p)
                # 存入智库

            # mongo_client.rm_person_by_id(p['_id'])
            mongo_client.update_person_by_id(str(p['_id']))
            del p['_id']
    infoCrawler.shutdown_crawlers()
    return persons_info

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



import json

from bs4 import BeautifulSoup
from bson import ObjectId

from EItools.classifier_mainpage.Extract import Extract
from EItools.client.mongo_client import  mongo_client
from EItools.extract.interface import interface
from EItools.extract import util
from EItools.detail_apart import detail_apart
from EItools import settings
from EItools.utils import chinese_helper
from EItools.chrome.crawler import InfoCrawler
import time
from time import strftime
from EItools.crawler import crawl_mainpage, search_items
from EItools.log.log import logger
from EItools import celery_app
import csv
import os
import heapq
import requests
import re

def get_data_from_aminer(person):
    post_json = {
        "action": "search.search", "parameters": {"advquery": {
            "texts": [{"source": "name", "text": ""}, {"source": "org", "text": ""}]},
            "offset": 0, "size": 10, "searchType": "SimilarPerson"},
        "schema": {
            "person": ["id", "name", "name_zh", "profile.affiliation", "avatar", "profile.affiliation_zh",
                       "profile.position","profile.email" "profile.position_zh", {"indices": ["hindex", "pubs", "citations"]}]}
    }
    url = "https://apiv2.aminer.cn/magic"
    headers = {
        'Content-Type':"application/json",
        'Debug':"1",
        'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyLXpuVGk4SlwvVzlYMkVIS1k5MTgwVTRnb2RHR0pzR3hDKzVPdmhWK25rWkMrSG1WZE1cL1JqSkdYeEdPQ2Q4TW9PNzFmS0lkeGxGb2s0QU8zZjBCZkxrZHp2YnZOblwvQzh6NUV2Vml6NmhrIiwidWlkIjoiNTZhMDQyYmVjMzVmNGY2NWY3N2Y3OGRiIiwic3JjIjoiYW1pbmVyIiwicm9sZXMiOlsicm9zdGVyX2VkaXRvciJdLCJpc3MiOiJhcGkuYW1pbmVyLm9yZyIsImV4cCI6MTU0MjI2MTA5MiwiaWF0IjoxNTM5NjY5MDkyLCJqdGkiOiJiYWEzZWE2MDA3NTU5NzZjY2YwZTY1YmI0MzVkYTQyY2Q1YjU2YmNiZTgwZWUzNmNlN2UyNDI5YWNmYzBhOGNiY2NhN2M0MWFhNmM0ZDc1ZTU3MjgyNDhkZDIzN2Q4NzBmYWU5NDMxYTE2OGU4YTQyNzNmMGY0YWIyNjBhMDNlODIzYWEwMWJmYTI3NzViZGVmMGQyZjFmYWJjZGNmOGI2NjdjNzY3YjYwNjNlYTJlNTk5MThhZDljZTUwZWVhNTVlYmE5ZDY0OTQ3MjU5OTJkMGNlZTMwMGU5ZjA1NGMzNmYzMGY2NjU4ZjVhNzNmYmZhYjU4YmNiZWE1M2FlZGVhIiwiZW1haWwiOiIyNzE4NTgzNzQxQHFxLmNvbSJ9.gws9Q4aow34EtggsY35gtEPg6aklbU8WgEh0BkvVOig'}
    try:
        post_json['parameters']['advquery']['texts'][0]['text'] = person['name']
        post_json['parameters']['advquery']['texts'][1]['text'] = person['org']
        resp = requests.post(url, headers=headers, json=[post_json])
        ok, result = get_resp_result(resp)
        print(ok)
        if ok and 'items' in result["data"][0]:
            sleepTime = 0  # have data, don't sleep
            for candidate in result["data"][0]["items"]:
                if 'profile' in candidate and 'affiliation' in candidate['profile']:
                    org = candidate['profile']['affiliation']
                elif 'profile' in candidate and 'org' in candidate['profile']:
                    org = candidate['profile']['org']
                else:
                    org = ''
                if 'name_zh' in candidate:
                    person_name = candidate['name_zh']
                    if person_name==person['name'] and (person['org'] in org or org in person['org']) :
                        person['aminer_url']="https://www.aminer.cn/profile/%s"%candidate['id']
                        if 'profile' in candidate and 'email' in candidate['profile']:
                            person['email']=candidate['profile']['email']
                        if 'profile' in candidate and 'position' in candidate['profile']:
                            person['position']=candidate['profile']['position']

                        return True, person
    except Exception as e:
        logger.error("%s, %s", "request aminer query error", e)
    return False, person

def select(r):
    if r['url']=="http://www.siom.ac.cn/":
        print(1)
    return r['label'] == 1 and r['score'] > 0.6 and ('kaoyan' not in r['domain'] if 'domain' in r else True) and ('kaoyan' not in r['url'] if 'url' in r else True) and ('考研' not in r['title'] if 'title' in r else True) and ('考研' not in r['text'] if 'text' in r else True)

def select_website(r):
    return len(re.findall('ac\.cn|edu\.cn|cas\.cn|baike',r['url'] if 'url' in r else ""))>0 or len(re.findall('ac\.cn|edu\.cn|cas\.cn|baike',r['domain'] if 'domain' in r else ""))>0

def get_data_from_web(person,info_crawler):
    success, person_of_aminer = get_data_from_aminer(person)
    if success:
        person['source'] = 'aminer'
    p=person

    result = search_items.Get('{},{}'.format(person['name'], person['org']))['res']
    #result_without_org = search_items.Get('{},'.format(person['name']))['res']
    result_rest = list(filter(select, result))
    result_rest=list(filter(select_website,result_rest))


    #result_without_org_rest = list(filter(select, result_without_org))
    # final_result=[]
    # for r in result_rest:
    #     for j in result_without_org_rest:
    #         print("{}_{}".format(r['url'], j['url']))
    #         if r['domain']==j['domain']:
    #             final_result.append(r)
    # mongo_client.db['search'].update({"_id": p['_id']}, {"$set": {"result": result}})
    # p['result'] = final_result if len(final_result)>0 and else result_rest
    # rare_value = int(util.get_name_rare(person['name']))
    # # if len(final_result)>0:
    # # 罕见度高,选取最新的
    # if rare_value <= 5:
    #     result_sorted = result_without_org_rest
    # else:
    #     result_sorted = result_rest
        # 罕见度低，选取公共的
        # else:
        #     p['result']=result_rest
        # 罕见度低，选取公共的
    # positive_result=[ r for r in result['res'] if r['label']==1.0]
    #if len(result_sorted) > 0:
    for se in result_rest:
        se['last_time'] = crawl_mainpage.get_lasttime_from_mainpage(se['url'])
    result_sorted_final = sorted(result_rest, key=lambda s: s['last_time'], reverse=True)
    #result_sorted_final=result_rest
    p['raw_result']=result
    p['result'] = result_sorted_final
    if len(result_sorted_final) > 0:
        selected_item = result_sorted_final[0]
        p['url'] = selected_item['url']
        p['source'] = 'crawler'
        p['info'] = crawl_mainpage.get_main_page(p['url'], person)
        logger.info("url is****{}".format(p['url']))

        # if util.compare(p['org'],se['domain'] if 'domain' in se else se['url']) or 'baidu.com' in se['url']:
        #     selected_item=se
        #     break
    #info, url = infoCrawler.get_info(person)
    citation, h_index, citation_in_recent_five_year = info_crawler.get_scholar_info(person)
    # # if affs is not None:
    # # p['s_aff'] = affs
    # #p['url'] = url
    # # p['info'] = info
    p['citation'] = citation
    p['h_index'] = h_index
    #p = extract_information.extract(info, p)
    if 'info' in p:
        apart_text(p)
        #if 'email'not in p and p['email']=="" and 'url' in p and p['url']!="" and len(re.findall('(edu.cn|cas.cn)',p['url']))<1:
    emails_prob = info_crawler.get_emails(person)
    p['source'] = 'crawler'
    p['emails_prob'] = emails_prob
    if ('email' not in p or p['email']=="") and len(p['emails_prob']) > 0:
        p['email'] = p['emails_prob'][0][0]

    return p

def apart_text(p):
    apart_result = interface(p['info'])
    PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ, AFF_ALL = apart_result if apart_result is not None else (
        None, None, None, None, None, None, None, None, None, None, None, None, None)
    honors = re.findall(
        '(长江学者|国家杰出青年|国家杰青|中科院百人计划|中国科学院百人计划|万人计划|国务院.*?政府特殊津贴|省部级以上科研院所二级研究员|973.*?首席科学家[\s\.。,，;；]+|863领域专家|百千万人才工程.*?人选者|创新人才推进计划|中国工程院院士|中国科学院院士|诺贝尔奖|图灵奖|菲尔兹奖)',
        p['info'])
    p['birth_time']=util.find_birthday(p['info'])
    p['mobile']=' '.join(util.find_phone_number(p['info']))
    p['degree'],p['diploma']=util.find_degree_and_diploma(p['info'])
    p['honors'] = list(set(honors))
    p['title'] = ""
    p['position'] = ','.join(JOB) if JOB is not None else ""
    search_items=re.search(p['name'], p['info'])
    if search_items is not None:
        name_first_position=search_items.span()[0]
        text_part_info=p['info'][name_first_position:name_first_position+70]
        p['title']+=','.join(set(Extract.extrac_title(text_part_info)))
        p['position']+= ','.join(set(Extract.extrac_position(text_part_info)+JOB))
    p['research'] = ','.join(DOM) if DOM is not None else ""
    p['edu_exp_region'] = ','.join(EDU) if EDU is not None else ""
    p['exp_region'] = ','.join(WRK) if WRK is not None else ""
    p['academic_org_exp_region'] = ','.join(SOC) if SOC is not None else ""
    p['awards_region'] = ','.join(AWD) if AWD is not None else ""
    p['patents_region'] = ','.join(PAT) if PAT is not None else ""
    p['projects_region'] = ','.join(PRJ) if PRJ is not None else ""
    p['gender'] = util.find_gender(p['info'])
    email = util.find_email(p['info'])
    p['email'] = email[0] if len(email) > 0 else ""
    p['edu_exp'] = detail_apart.find_edus(p['edu_exp_region'])
    p['exp'] = detail_apart.find_works(p['exp_region'])
    p['academic_org_exp'] = detail_apart.find_socs(p['academic_org_exp_region'])
    p['awards'] = detail_apart.find_awards_list(AWD)
    p['patents'] = detail_apart.find_patents(p['patents_region'])
    p['projects'] = detail_apart.find_projects(p['projects_region'])
    p['pubs']=detail_apart.fetch_pubs_from_webpage(p['info'])
    p['aff'] = {}
    current_aff = []
    if AFF is not None and len(AFF) > 0:
        for aff in AFF:
            current_aff.append(aff)
    if AFF_ALL is not None:
        for aff in AFF_ALL:
            print("aff-{}".format(aff))
            try:
                aff_filter = aff.replace('(', '\(').replace(')', '\)').replace('[', '\[').replace(']',
                                                                                                  '\]').replace(
                    '+', '\+').replace('\\r', '\\\\r')
                pattern = '(现为|至今|现任职于|现任|-今于|目前为|现为|工作单位|-今|现在|当前){1,2}[\s\S]{0,5}' + aff_filter
                filter_pattern=r'(大学|研究院|公司|研究所|科学院)'
                result = re.search(pattern, p['info'])
                if result is not None:
                    if len(re.findall(filter_pattern,aff))>0:
                        current_aff.append(aff)
                else:
                    pattern_back = aff_filter + '[\s\S]{0,5}(至今){1,2}'
                    result = re.search(pattern_back, p['info'])
                    if result is not None:
                        if len(re.findall(filter_pattern, aff)) >0:
                            current_aff.append(aff)
            except Exception as e:
                logger.error("when find current aff:{}".format(e))
    if len(current_aff) > 0:
        p['aff']['inst'] = ' '.join(set(current_aff))
    if 'inst' not in p['aff'] or p['aff']['inst']=="":
        p['aff']['inst']=p['org']
    return p

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
        post_json['parameters']['advquery']['texts'][1]['text'] = person['org']
        resp = requests.post(url, headers=headers, json=[post_json])
        ok, result = get_resp_result(resp)
        print(ok)
        if ok and 'items' in result["data"][0]:
            return ok
    except Exception as e:
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

def crawl_google_scholar(person):
    citation, h_index, citation_in_recent_five_year = info_crawler.get_scholar_info(person)
    return h_index

info_crawler = InfoCrawler()
info_crawler.load_crawlers()
@celery_app.task
def crawl_person_info(persons,task_id,from_api=False):
    persons_info = []
    for i, p in enumerate(persons):
        if 'name' in p:
            # person = {}
            # person['name'] = p['name']
            # # affs = pre_process.get_valid_aff(p['org'])
            # # person['org'] = ' '.join(affs)
            # person['org'] = p['org']
            print("id is {}".format(p['id']))
                # mongo_client.save_crawled_person(p1)
            p['_id']=ObjectId(p['id'])
            p['task_id']=ObjectId(task_id)
            p=get_data_from_web(p,info_crawler)
            mongo_client.save_crawled_person(p)
                # 存入智库
            # mongo_client.rm_person_by_id(p['_id'])
            if task_id is not None:
                mongo_client.update_person_by_id(str(p['_id']),task_id)
            if from_api:
                del p['_id']
                persons_info.append(p)
    #info_crawler.shutdown_crawlers()
    return persons_info









import json

from EItools.client.mongo_client import MongoDBClient
from EItools.extract.interface import interface
from EItools.extract import util
from EItools.detail_apart import detail_apart
from EItools import settings
from EItools.utils import chinese_helper
from EItools.chrome.crawler import InfoCrawler
import time
from time import strftime
from EItools.crawler import crawl_mainpage, process
from EItools.log.log import logger
import csv
import os
import requests
import re

mongo_client=MongoDBClient()

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
                if 'name' in candidate:
                    person_name = candidate['name']
                    sim_name = chinese_helper.simila_name(person_name, person['name'])
                    sim_aff = chinese_helper.simila_name(org, ''.join(person['org']))
                    if sim_name > 0 and sim_aff > 0:
                        return True, candidate
    except Exception as e:
        print(e)
        logger.error("%s, %s", "request url error", e)
    return False, person

def get_data_from_web(person,info_crawler):
    p=person
    def select(r):
        return r['label'] == 1 and r['score'] > 0.8

    result = process.Get('{},{}'.format(person['name'], person['org']))['res']
    result_without_org = process.Get('{},'.format(person['name']))['res']
    result_rest = list(filter(select, result))
    result_without_org_rest = list(filter(select, result_without_org))
    # final_result=[]
    # for r in result_rest:
    #     for j in result_without_org_rest:
    #         print("{}_{}".format(r['url'], j['url']))
    #         if r['domain']==j['domain']:
    #             final_result.append(r)
    # mongo_client.db['search'].update({"_id": p['_id']}, {"$set": {"result": result}})
    # p['result'] = final_result if len(final_result)>0 and else result_rest
    rare_value = int(util.get_name_rare(person['name']))
    # if len(final_result)>0:
    # 罕见度高,选取最新的
    if rare_value <= 5:
        result_sorted = result_without_org_rest
    else:
        result_sorted = result_rest
        # 罕见度低，选取公共的
        # else:
        #     p['result']=result_rest
        # 罕见度低，选取公共的
    # positive_result=[ r for r in result['res'] if r['label']==1.0]
    if len(result_sorted) > 0:
        for se in result_sorted:
            se['last_time'] = crawl_mainpage.get_lasttime_from_mainpage(se['url'])
    result_sorted_final = sorted(result_sorted, key=lambda s: s['last_time'], reverse=True)
    p['result'] = result_sorted_final
    if len(result_sorted_final) > 0:
        selected_item = result_sorted_final[0]
        p['url'] = selected_item['url']
        p['source'] = 'crawler'
        p['info'] = crawl_mainpage.get_main_page(p['url'], person)
        print("url is****" + p['url'])

        # if util.compare(p['org'],se['domain'] if 'domain' in se else se['url']) or 'baidu.com' in se['url']:
        #     selected_item=se
        #     break
    # info, url = infoCrawler.get_info(person)
    emails_prob = info_crawler.get_emails(person)
    #citation, h_index, citation_in_recent_five_year = info_crawler.get_scholar_info(person)
    # if affs is not None:
    # p['s_aff'] = affs
    # p['url'] = url
    # p['info'] = info
    #p['citation'] = citation
    #p['h_index'] = h_index
    # p = extract_information.extract(info, p)
    if 'info' in p:
        apart_result = interface(p['info'])
        PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ, AFF_ALL = apart_result if apart_result is not None else (
            None, None, None, None, None, None, None, None, None, None, None, None)
        honors=re.findall(
            '(国家杰出青年|国家杰青|百人计划|国务院政府特殊津贴|省部级以上科研院所二级研究员|973首席科学家|863|百千万人才工程国家级人选|创新人才推进计划|中国工程院院士|中国科学院院士|诺贝尔奖|图灵奖|菲尔兹奖)', p['info'])
        p['honors']=list(set(honors))
        p['aff'] = {}
        if AFF is not None:
            p['aff']['inst'] = ' '.join(AFF)
        else:
            current_aff = []
            for aff in AFF_ALL:
                print("aff-{}".format(aff))
                try:
                    aff_filter = aff.replace('(', '\(').replace(')', '\)').replace('[', '\[').replace(']',
                                                                                                      '\]').replace(
                        '+', '\+').replace('\\r', '\\\\r')
                    pattern = '((现为)|(至今)|(现任职于)|(现任)|(-今于)|(目前为)|(现为)|(工作单位)|(-今)){1,2}[\s\S]{0,5}' + aff_filter
                    result = re.search(pattern, p['exp_region'])
                    if result is not None:
                        current_aff.append(aff)
                    else:
                        pattern_back = aff_filter + '[\s\S]{0,5}((至今)){1,2}'
                        result = re.search(pattern_back, p['exp_region'])
                        if result is not None:
                            current_aff.append(aff)
                except Exception as e:
                    print(e)
            if len(current_aff) > 0:
                p['aff']['inst'] = ' '.join(current_aff)

        p['title'] = ''.join(TIT) if TIT is not None else ""
        p['position'] = ''.join(JOB) if JOB is not None else ""
        p['domain'] = ''.join(DOM) if DOM is not None else ""
        p['edu_exp_region'] = ''.join(EDU) if EDU is not None else ""
        p['exp_region'] = ''.join(WRK) if WRK is not None else ""
        p['academic_org_exp_region'] = ' '.join(SOC) if SOC is not None else ""
        p['awards_region'] = ''.join(AWD) if AWD is not None else ""
        p['patents_region'] = ''.join(PAT) if PAT is not None else ""
        p['projects_region'] = ''.join(PRJ) if PRJ is not None else ""
        p['gender'] = util.find_gender(p['info'])
        email = util.find_email(p['info'])
        p['email'] = email[0] if len(email) > 0 else ""
        p['edu_exp'] = detail_apart.find_edus(p['edu_exp_region'])
        p['exp'] = detail_apart.find_works(p['exp_region'])
        p['academic_org_exp'] = detail_apart.find_socs(p['academic_org_exp_region'])
        p['awards'] = detail_apart.find_awards_list(AWD)
        p['patents'] = detail_apart.find_patents(p['patents_region'])
        p['projects'] = detail_apart.find_projects(p['projects_region'])
    p['source'] = 'crawler'
    p['emails_prob'] = emails_prob
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

def crawl_person_info(persons,task_id,from_api=False):
    info_crawler = InfoCrawler()
    info_crawler.load_crawlers()
    persons_info = []
    for i, p in enumerate(persons):
        if 'name' in p:
            # person = {}
            # person['name'] = p['name']
            # # affs = pre_process.get_valid_aff(p['org'])
            # # person['org'] = ' '.join(affs)
            # person['org'] = p['org']
            success, person_of_aminer = get_data_from_aminer(p)
            if False:
                p = person_of_aminer
                p['source'] = 'aminer'
                # mongo_client.save_crawled_person(p1)
            else:
                p=get_data_from_web(p,info_crawler)
                mongo_client.crawed_person_col.save(p)
                # 存入智库
            # mongo_client.rm_person_by_id(p['_id'])
            if task_id is not None:
                mongo_client.update_person_by_id(str(p['_id']),task_id)
            if from_api:
                del p['_id']
                persons_info.append(p)
    info_crawler.shutdown_crawlers()
    return persons_info
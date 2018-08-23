import json

import logging
import urllib.request
import urllib.parse

import re
import requests
import sys

from EItools.log.log import logger
from EItools.utils import common_utils


class RESTClient(object):
    def __init__(self):
        self.base_url = "https://api.aminer.org/api/"

    def get_url(self, url):
        return self.base_url + url

    def get_person(self, id):
        resp = common_utils.rest_get(self.get_url("person/%s" % id))
        return resp.json()

    def get_experts(self, ebid, offset, size):
        resp = common_utils.rest_get(
            self.get_url("roster/%s/order-by/h_index/offset/%s/size/%s" % (ebid, offset, size)))
        # resp = requests.get(self.get_url("roster/%s/order-by/h_index/offset/%s/size/%s" % (ebid, offset, size)))
        experts = resp.json()
        return experts

    def get_all_experts(self, ebid, size=50):
        for item in common_utils.iterate_pages(self.get_experts, ebid, is_list=False, size=size, k_data="result",
                                               k_total="total"):
            yield item
        # offset = 0
        # experts = []
        # while True:
        #     data = self.get_experts(ebid, offset, size)
        #     if data["total"] < offset:
        #         break
        #     experts.extend(data["result"])
        #     offset += size
        # return experts

    def get_institution(self, iid):
        resp = common_utils.rest_get(self.get_url("aff/summary/%s" % iid))
        return resp.json()

    def get_ins_members(self, iid, offset=0, size=0):
        # resp = common_utils.rest_get(self.get_url("aff/iid/%s/members/offset/%s/size/%s" % (iid, offset, size)))
        resp = common_utils.rest_get(self.get_url("roster/%s/order-by/h_index/offset/%s/size/%s" % (iid, offset, size)))
        return resp.json()

    def get_ins_pubs(self, iid, offset=0, size=0):
        # https://api.aminer.org/api/search/pub/inst/575f9e5976d91118a4b492b1?offset=0&size=50
        user_agent = {'User-agent': 'Mozilla/5.0'}
        resp = requests.get(self.get_url("search/pub/inst/%s?offset=%s&size=%s" % (iid, offset, size)),
                            headers=user_agent)
        # resp = requests.get(self.get_url("aff/pubs/iid/%s/all/cite/offset/%s/size/%s" % (iid, offset, size)))
        return resp.json()

    def search_person(self, query, offset=0, size=30):
        user_agent = {'User-agent': 'Mozilla/5.0'}
        resp = requests.get(self.get_url("search/person?query=%s&offset=%s&size=%s" % (query, offset, size)),
                            headers=user_agent)
        return resp.json()

    def search_pub_advanced(self, query, offset=0, size=20):
        resp = common_utils.rest_get(self.get_url("search/pub/advanced?name={}&offset={}&org={}&size={}&term={}&sort={}".format(query.get('name', ''), offset, query.get('org', ''), size, query.get('term', ''), query.get('sort', ''))))
        return resp.json()

    def search_pub_advanced_all(self, term="", name="", org="", sort="", size=20):
        query = {
            'term': term,
            'name': name,
            'org': org,
            'sort': sort
        }
        for item in common_utils.iterate_pages(self.search_pub_advanced, query, is_list=False, size=size, k_data="result", k_total="total"):
            yield item

    def get_ins_all_pubs(self, iid, size=50):
        offset = 0
        pubs = []
        while True:
            data = self.get_ins_pubs(iid, offset, size)
            if data["size"] < offset:
                break
            pubs.extend(data["result"])
            offset += size
        return pubs

    def get_ins_pubs_1(self, iid, offset=0, size=0):
        # https://api.aminer.org/api/search/pub/inst/575f9e5976d91118a4b492b1?offset=0&size=50
        user_agent = {'User-agent': 'Mozilla/5.0'}
        # resp = requests.get(self.get_url("search/pub/inst/%s?offset=%s&size=%s" % (iid, offset, size)), headers=user_agent)
        resp = requests.get(self.get_url("aff/pubs/iid/%s/all/cite/offset/%s/size/%s" % (iid, offset, size)),
                            headers=user_agent)
        return resp.json()

    def get_ins_all_pubs_1(self, iid, size=30):
        offset = 0
        pubs = []
        cnt = 0
        while True:
            data = self.get_ins_pubs_1(iid, offset, size)
            if data["size"] < offset:
                break
            pubs.extend(data["data"])
            cnt += len(data["data"])
            print(offset, data["size"], cnt, len(data["data"]))
            offset += size
        return pubs

    def get_ins_projects(self, iid, offset=0, size=0):
        resp = common_utils.rest_get(self.get_url("aff/projects/iid/%s/all/offset/%s/size/%s" % (iid, offset, size)))
        return resp.json()

    def get_ins_patents(self, iid, offset=0, size=0):
        resp = common_utils.rest_get(self.get_url("aff/patents/iid/%s/all/offset/%s/size/%s" % (iid, offset, size)))
        return resp.json()

    def get_person_pubs(self, pid, offset=0, size=0):
        resp = common_utils.rest_get(self.get_url("person/pubs/%s/all/year/%s/%s" % (pid, offset, size)))
        return resp.json()

    def get_person_pub_all(self, pid, total):
        for item in common_utils.iterate_pages(self.get_person_pubs, pid, total=total):
            yield item

    def get_ins_pubs_by_label(self, iid, label, offset=0, size=0):
        resp = common_utils.rest_get(
            self.get_url(
                "search/pub/inst/%s?labels=%s&offset=%s&size=%s" % (iid, label, offset, size)
                # "aff/pubs/tag/%s/iid/57d2043c2abe00ce522da340/all/offset/%s/size/%s" % (label, offset, size)
            )
        )
        return resp.json()

    def get_ins_pubs_by_label_1(self, iid, label, offset=0, size=0):
        user_agent = {'User-agent': 'Mozilla/5.0'}
        resp = common_utils.rest_get(
            self.get_url(
                # "search/pub/inst/552e0af6dabfae7de9e77cf6?labels=%s&offset=%s&size=%s" % (label, offset, size)
                "aff/pubs/tag/%s/iid/%s/all/offset/%s/size/%s" % (label, iid, offset, size)
            ))
        return resp.json()

    def get_pubs_by_label_all(self, label):
        for item in common_utils.iterate_pages(self.get_ins_pubs_by_label, label, k_data="result", k_total="size",
                                               is_list=False):
            yield item

    def assign_pub_to_claim(self, aid, pid, order):
        resp = common_utils.rest_post(self.get_url("person/pubs/%s/tobeconfirmed/%s/%s" % (str(aid), str(pid), order))).json()
        if "status" in resp and resp["status"]:
            return True
        else:
            print("error", aid, pid, resp["status"])
            return False

    def search(self,name,org):
        post_json ={
                    "action": "search.search",
                    "parameters": {
                        "advquery": {
                            "texts": [
                                {
                                    "source": "name",
                                    "text": ""
                                },
                                {
                                    "source": "org",
                                    "text": ""
                                }
                            ]
                        },
                        "offset": 0,
                        "size": 10,
                        "searchType": "SimilarPerson"
                    },
                    "schema": {
                        "person": [
                            "id",
                            "name",
                            "name_zh",
                            "profile.affiliation",
                            "avatar",
                            "profile.affiliation_zh",
                            "profile.position",
                            "profile.position_zh",
                            {
                                "indices": [
                                    "hindex",
                                    "pubs",
                                    "citations"
                                ]
                            }
                        ]
                    }
                }

        post_json["parameters"]["advquery"]["texts"][0]["text"]=name
        post_json["parameters"]["advquery"]["texts"][1]["text"] = org
        url = "https://apiv2.aminer.cn/magic"
        urls = {"local": url, "beta": "https://apiv2-beta.aminer.org/magic",
                "product": "https://apiv2.aminer.cn/magic"}
        headers = {
            'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyLXZBZWJMNnB3YVdZQnVuc1ZXQVhIUkF0MjAyWmhpSFpoamtVUkFDWE5ENTBXRGVPTUlVRE1kMDgxTTBOVGhxRDY4YnVtM2U2K2RtOWxReWJlWUtVOVM3ZVRmTEx1dlp4djY2VVNpY0lpIiwidWlkIjoiNTZhMDQyYmVjMzVmNGY2NWY3N2Y3OGRiIiwic3JjIjoiYW1pbmVyIiwicm9sZXMiOlsicm9zdGVyX2VkaXRvciJdLCJpc3MiOiJhcGkuYW1pbmVyLm9yZyIsImV4cCI6MTUyNzA1NzYyMiwiaWF0IjoxNTI0NDY1NjIyLCJqdGkiOiI5ZWRhM2Y4NjBiZTIyZGY4MjIxNzk3Nzk1NTAzMDIyMjc2NmFkZTAzODUzMzkzZTEwZDgxYmM1YjY5NmZiODkzNTFjZjg1NTYxNTM3OGE3OWU5OGVkNDdkODdlNWQ3NDZlMmI2ZWNlMjcwYWUzOWQ5ZTMyZDJkNTkyNDI0N2Q2OTc3YWFkYWZjOWZkNzk4YmI4MzFlMDNjMjUzMDVkNGUxYzM0MWM4MTc0MjAxNTVhNjM5OTc2NTMxMzRhYzczNGFmOTdiMmI3MzVjMzJjNmQ2NThhZjI5OWJhNjJiY2EzNDZhMTE4YzM1ZjVlYTU5YWExZmRmYmUwYWJmMWY5ZWQ3IiwiZW1haWwiOiIyNzE4NTgzNzQxQHFxLmNvbSJ9.iBC_bXb97O6RiBmvZGjgky36_1W-qN3imhRCTx7bf1s'}

        resp = requests.post(url, headers=headers, json=[post_json])
        ok, result = self.get_resp_result(resp)

        if ok and 'items' in result["data"][0]:
            for person in result["data"][0]["items"]:
               yield person

    def get_resp_result(self,resp):
        if resp.status_code == 200:
            result = json.loads(resp.text)
            if result["data"][0]["succeed"]:
                return True, result
        else:
            logging.error("request %s error: %s", resp.url, resp.text)
        return False, None


    def recognize_entity(self,text):
        p = re.compile('\n', re.S)
        post_json={"index_choose":"zh","text":""}
        url = "http://xlink.xlore.org/linkingSubmit.action"
        post_json["text"]=text
        data=urllib.parse.urlencode(post_json)
        result = []
        try:
            resp = urllib.request.Request(url,bytes(data,encoding="utf-8"))
            response = urllib.request.urlopen(resp)
            s=json.loads(str(response.read(),encoding="utf8"))
            if len(s["ResultList"])>0:
                for r in s["ResultList"]:
                    result.append(r["label"])
            else:
                if text is not None:
                    result.append(text)
                else:
                    result.append("")
        except Exception as e:
            logger.info(e)
        return result




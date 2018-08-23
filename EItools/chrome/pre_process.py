import re

from EItools.client.rest_client import RESTClient
from EItools.log.log import logger
from EItools.utils import chinese_helper

rest_client=RESTClient()
def get_valid_aff(org):
    if chinese_helper.contain_zh(org):
        affiliation = chinese_helper.translate(org, 'zh', 'zh')
    else:
        affiliation = chinese_helper.translate(org, 'en', 'zh')
    logger.info(affiliation)
    affs = [s for s in rest_client.recognize_entity(affiliation) if
            s.find("大学") != -1 or s.find("公司") != -1 or s.find("中心") != -1
            or s.find("医院") != -1 or s.find("研究") != -1]
    if len(affs) == 0:
        if affiliation is not None:
            affs = re.split(r'，|、|\\s', affiliation)
        if len(affs) >0:
            affs = [s for s in affs if (s.find("大学") != -1 or s.find("公司") != -1 or s.find("中心") != -1
                    or s.find("医院") != -1 or s.find("研究") != -1)]
        else:
            affs.append(affiliation)
    else:
        affs.append(affiliation)
    return list(set(affs))


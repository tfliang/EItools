import os, sys, re

from EItools.client.mongo_client import MongoDBClient, mongo_client

DATA_DIR = os.path.join(os.path.abspath('..'), 'data')

def clean_text(text):
    if text is not None:
        text = text.replace('\xa0', '').replace('\u3000', '').strip()#.replace('\n', '')
    return text

def clean_word(text):
    text = text.replace('\xa0', '').replace('\u3000', '').strip()#.replace('\n', '')
    text = re.sub(r'<[/a-zA-Z]+>', '', text)
    text = re.sub(r'[a-zA-Z]*<[/a-zA-Z]*', '', text)
    text = re.sub(r'[/a-zA-Z]*>[a-zA-Z]*', '', text)
    # text = text.replace('<', '')
    # text = text.replace('>', '')
    return text

def clean_list(lst):
    new_lst = []
    for item in lst:
        if check_contain_chinese(clean_word(item)):
            new_lst.append(clean_word(item))
    return list(set(new_lst))

def clean_list_sec(lst):
    for i, item in enumerate(lst):
        lst[i] = clean_word(item)
    return lst

def remove_dup(lst):
    return list(set(lst))

def remove_sign(lst):
    for i, item in enumerate(lst):
        lst[i] = re.sub(r'<[/a-zA-Z]+?>', '', item)
    return lst


def check_contain_chinese(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def extract(name, text):
    pattern = re.compile(r'<' + name + r'>([^<>]+)</' + name + r'>')
    return remove_dup(pattern.findall(text))

def find_gender(text):
    if '男' in text:
        return '男'
    elif '女' in text:
        return '女'
    else:
        return ""

def find_birthday(text):
    pattern = re.compile(r'生\s*?[于年月]*[\.。,，:：\s]*((?:19|20)[0-9]{2}[年|.|/]?[0-9]{0,2}[月]?)[\s\.。,，;；]+')
    pattern_other=re.compile(r'((?:19|20)[0-9]{2}[年|.|/]?[0-9]{0,2}[月]?)[出]?生')
    search_item=pattern.search(text)
    if search_item is not None:
        birth_time=search_item.group(0)
        return birth_time
    else:
        search_item=pattern_other.search(text)
        if  search_item is not None:
            return search_item.group(0)

def find_name(text, PER):
    min_idx = 100000000000
    res = None
    for name in PER:
        if name in text and text.index(name) < min_idx:
            min_idx = text.index(name)
            res = name
    return remove_sign([res])

def find_aff(text, ORG):
    min_idx = 100000000000
    res = None
    for org in ORG:
        if org in text and text.index(org) < min_idx:
            min_idx = text.index(org)
            res = org
    return remove_sign([res])


def find_email(text):
    res = re.search(r'[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+', text)
    if res != None:
        return remove_sign([res.group()])
    else:
        return []

def find_phone_number(text):
    res = re.search(r'(电话|联系方式)[\.。,，:：\s]*\d{1}(.+?)[\s\.。,，;；]+',text)
    if res != None:
        return remove_sign([res.group()])
    else:
        return []


def find_degree_and_diploma(text):
    degree = ""
    diploma = ""
    if '本科' in text or '学士' in text:
        degree = '学士'
    if '研究生' in text or '硕士' in text:
        degree = '硕士'
    if '博士' in text or '博士后' in text:
        degree = '博士'
    if degree == '学士':
        diploma = '本科'
    elif degree == '博士' or degree == '硕士':
        diploma = '研究生'
    return degree,diploma


def find_address(text):
    pattern = re.compile(r'地\s*?址[\.。,，:：\s]*([^\n\.。,，:：;；个]+?)[\s\.。,，;；]')
    return remove_sign(pattern.findall(text))

def find_title(text):
    pattern = re.compile(r'职\s*?[称位][\.。,，:：\s]*(.+?)[\s\.。,，;；]')
    return remove_sign(pattern.findall(text))

def find_work_detail(text):
    pattern=re.compile(r'\d')

def compare(org, url):
    if org!="" and url!="":
        aff = mongo_client.db['aff'].find_one({"name": org})
        if aff is not None and aff['domain'] != "":
            domain_key = aff['domain'].replace("https://", "").replace("http://", "").split('.')[1]
            item_key = url.replace("https://", "").replace("http://", "")
            if domain_key in item_key:
                return True
    return False
def get_name_rare(name):
    person=mongo_client.db['name_rare'].find_one({'name':name})
    if person is not None:
        return person['rare']
    else:
        return 3

if __name__ == "__main__":
    # with open(os.path.join(DATA_DIR, 'infoExample2000-2100.txt')) as file:
    #     data = file.read()
    # personList = data.split('*********&&&&&&&&')
    # print(clean_text(personList[0]))
    # print(check_contain_chinese('中国'))
    # print(check_contain_chinese('xxx'))
    # print(check_contain_chinese('xx中国'))
    #print(compare("中国科学技术大学","http://dsxt.ustc.edu.cn/zj_js.asp?zzid=992"))
    #print(find_degree_and_diploma("安景文，男，满族，1964年3月生，1990年8月参加工作，1993年4月加入中国共产党，研究生学历，硕士学位，研究员，现任辽宁省农业科学院科研管理处处长，拟任辽宁省农业科学院党组成员、总农艺师"))
    print(find_title("职称 :研究员."))
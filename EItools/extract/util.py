import os, sys, re
DATA_DIR = os.path.join(os.path.abspath('..'), 'data')

def clean_text(text):
    text = text.replace('\xa0', '').replace('\u3000', '').strip()#.replace('\n', '')
    return text

def clean_word(text):
    text = text.replace('\xa0', '').replace('\u3000', '').strip().replace('\n', '')
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
        return ['男']
    elif '女' in text:
        return ['女']
    else:
        return []

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

def find_address(text):
    pattern = re.compile(r'地\s*?址[\.。,，:：\s]*([^\n\.。,，:：;；个]+?)[\s\.。,，;；]')
    return remove_sign(pattern.findall(text))

def find_title(text):
    pattern = re.compile(r'职\s*?[称位][\.。,，:：\s]*(.+?)[\s\.。,，;；]')
    return remove_sign(pattern.findall(text))

if __name__ == "__main__":
    # with open(os.path.join(DATA_DIR, 'infoExample2000-2100.txt')) as file:
    #     data = file.read()
    # personList = data.split('*********&&&&&&&&')
    # print(clean_text(personList[0]))
    print(check_contain_chinese('中国'))
    print(check_contain_chinese('xxx'))
    print(check_contain_chinese('xx中国'))
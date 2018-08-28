import os
import re

# from util import *

DATA_DIR = os.path.join(os.path.abspath('..'), 'data')


def clean_text(text):
    text = text.replace('\xa0', '').replace('\u3000', '')  # .replace('\n', '')
    text = re.sub(r'[\n]+', '\n', text)
    return text


tag = {
    # 'name' : 'PER',
    # 'address' : 'ADR',
    'aff' : 'AFF',
    'title': 'TIT',
    'job': 'JOB',
    'domain': 'DOM',
    'edu': 'EDU',
    'work': 'WRK',
    'social': 'SOC',
    'award': 'AWD',
    'patent': 'PAT',
    'project': 'PRJ'}
tag2label = {"O": 'O',
             # "B-PER": 'A', "I-PER": 'a',
             # "B-ADR": 'B', "I-ADR": 'b',
            "B-AFF": 'C', "I-AFF": 'c',
             "B-TIT": 'D', "I-TIT": 'd',
             "B-JOB": 'E', "I-JOB": 'e',
             "B-DOM": 'F', "I-DOM": 'f',
             "B-EDU": 'G', "I-EDU": 'g',
             "B-WRK": 'H', "I-WRK": 'h',
             "B-SOC": 'I', "I-SOC": 'i',
             "B-AWD": 'J', "I-AWD": 'j',
             "B-PAT": 'K', "I-PAT": 'k',
             "B-PRJ": 'L', "I-PRJ": 'l'
             }
label2tag = {"O": 'O', "X": 'X',
             # 'A': "B-PER", 'a': "I-PER",
             # 'B': "B-ADR", 'b': "I-ADR",
             'C': "B-AFF", 'c': "I-AFF",
             'D': "B-TIT", 'd': "I-TIT",
             'E': "B-JOB", 'e': "I-JOB",
             'F': "B-DOM", 'f': "I-DOM",
             'G': "B-EDU", 'g': "I-EDU",
             'H': "B-WRK", 'h': "I-WRK",
             'I': "B-SOC", 'i': "I-SOC",
             'J': "B-AWD", 'j': "I-AWD",
             'K': "B-PAT", 'k': "I-PAT",
             'L': "B-PRJ", 'l': "I-PRJ",
             }


def tagging(text,w):
    # print(text, len(text))
    mark = ['O'] * len(text)
    pattern = re.compile(r'(<([a-zA-Z]+?)>([^<>]+?)</[\\a-zA-Z]+?>)')
    if re.search(pattern, text) is None:
        return -1
    # print(text)
    while (1):
        pattern = re.compile(r'(<([a-zA-Z]+?)>([^<>]+?)</[\\a-zA-Z]+?>)')
        res = re.search(pattern, text)

        if res == None:
            break

        length = len(res.group(3))
        begin = res.span(1)[0]
        tag_name = res.group(2)
        # print(res.group(1), res.group(3), res.span(3), begin, length)
        text = re.sub(pattern, res.group(3), text, count=1)
        # print(text[begin:begin+length])
        if tag_name in tag:
            mark[begin] = tag2label['B-' + tag[tag_name]]
            for i in range(begin + 1, begin + length):
                mark[i] = tag2label['I-' + tag[tag_name]]
                # print(mark[140:160])

    # delete continuous O
    mark = list((''.join(mark)).replace('O' * 500, 'X' * 500))
    # print(mark, len(mark))
    new_line = True
    last=''
    for i, ch in enumerate(text):
        if ch == '\n':
            if i == 0 or last =='\n':
                continue
            if new_line:
                print('')
                w.write('\n')
                pass
                new_line = False
            last = '\n'
        else:
            new_line = True
            print(mark[i])
            if ch not in [' ', '\r', '\t', '\u2002', '\u2003', '\u2009'] and mark[i] != 'X':
                last=ch
                print(ch, '\t', label2tag[mark[i]])
                w.write(ch+'\t'+label2tag[mark[i]])
                w.write('\r\n')
                pass

    print('')
    return 0


def cut_text(text):
    punct = set(u''':!),:;?]}¢'"、。〉》」』〕〗〞︰︱︳﹐､﹒
    ﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､￠
    々‖•·ˇˉ―′’”([{£¥'"‵〈《「『〔〖（［｛￡￥〝︵︷︹︻-
    ︽︿﹁﹃﹙﹛﹝（｛“‘_…+|''')

    def cut_word(text):
        for p in punct:
            if p in text:
                text = text.replace(p, ' ')
        return text

    text = cut_word(text)

    find = re.search(r'[\./a-zA-Z0-9\s]{50,}', text)

    while (find != None):
        word = find.group()
        text = text.replace(word, '')
        find = re.search(r'[a-zA-Z0-9\s]{50,}', text)

    return text


train_data = ['info500-750.txt', '750-1000.txt', 'info1000-1250.txt', '1250-1500.txt', 'infoExample2000-2100.txt',
               'infoExample2100-2200.txt', 'infoExample2200-2300.txt', 'infoExample2400-2500.txt',
               'infoExample2600-2700.txt']
#train_data = ['info500-750.txt']
test_data = ['infoExample2700-2800.txt', 'infoExample2800-2900.txt']
with open(os.path.join(DATA_DIR, 'test_data'), 'w+') as w:
    for file_name in test_data:
        with open(os.path.join(DATA_DIR, file_name), 'r') as file:
            data = file.read()
        personList = data.split('*********&&&&&&&&')
        for i,text in enumerate(personList):
            #text=cut_text(text)
            tagging(clean_text(text),w)


        res = re.search(r'[\n]+', text)


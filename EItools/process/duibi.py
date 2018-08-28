from EItools.client.mongo_client import MongoDBClient

from EItools.extract.interface import interface

mongo_client=MongoDBClient()
persons=mongo_client.get_crawled_person(0,100)
def clean_word(text):
    text = text.replace('\xa0', '').replace('\u3000', '').strip().replace('\n', '')
    return text

def clean_list(lst):
    new_lst = []
    for item in lst:
        new_lst.append(clean_word(item))
    return list(set(new_lst))

def print_tag(lst, name, text):
    temp = clean_list(lst)
    text = clean_word(text)
    cnt = [text.count(word) for word in temp]
    string=name+': '
    for i, v in enumerate(temp):
        str1=str(temp[i]) + '(' + str(cnt[i]) + '),'
        string +=str1
    return string

with open('test_data6.txt','w+') as w:
    for id in persons:
        p=mongo_client.get_crawled_person_by_pid(id)
        if 'info' in p and p['info'] !="":
            text=p['info']
            w.write(id)
            w.write('\r\n')
            PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ=interface(p['info'])
            # w.write('PER:'+''.join(PER))
            # w.write('\r\n')
            # w.write('ADR:'+''.join(ADR))
            # w.write('\r\n')
            # w.write('AFF:'+''.join(AFF))
            # w.write('\r\n')
            # w.write('TITLE:'+''.join(TIT))
            # w.write('\r\n')
            # w.write('JOB:'+''.join(JOB))
            # w.write('\r\n')
            # w.write('DOM:'+''.join(DOM))
            # w.write('\r\n')
            # w.write('EDU:'+''.join(EDU))
            # w.write('\r\n')
            # w.write('WRK:'+''.join(WRK))
            # w.write('\r\n')
            # w.write('SOC'+''.join(SOC))
            # w.write('\r\n')
            # w.write('AWD'+''.join(AWD))
            # w.write('\r\n')
            # w.write('PAT'+''.join(PAT))
            # w.write('\r\n')
            # w.write('PRJ'+''.join(PRJ))
            # w.write('\r\n')
            str_list=[]
            if PER is not None:
                str1=print_tag(PER, 'PER', text)
                str_list.append(str1)
            if ADR is not None:
                str1=print_tag(ADR, 'ADR', text)
                str_list.append(str1)
            if AFF is not None:
                str1=print_tag(AFF, 'AFF', text)
                str_list.append(str1)
            if TIT is not None:
                str1=print_tag(TIT, 'TIT', text)
                str_list.append(str1)
            if JOB is not None:
                str1=print_tag(JOB, 'JOB', text)
                str_list.append(str1)
            if DOM is not None:
                str1=print_tag(DOM, 'DOM', text)
                str_list.append(str1)
            if EDU is not None:
                str1=print_tag(EDU, 'EDU', text)
                str_list.append(str1)
            if WRK is not None:
                str1=print_tag(WRK, 'WRK', text)
                str_list.append(str1)
            if SOC is not None:
                str1=print_tag(SOC, 'SOC', text)
                str_list.append(str1)
            if AWD is not None:
                str1=print_tag(AWD, 'AWD', text)
                str_list.append(str1)
            if PAT is not None:
                str1=print_tag(PAT, 'PAT', text)
                str_list.append(str1)
            if PRJ is not None:
                str1=print_tag(PRJ, 'PRJ', text)
                str_list.append(str1)
            w.write('\n'.join(str_list))
            w.write('######')




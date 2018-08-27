from EItools.client.mongo_client import MongoDBClient

from EItools.extract.interface import interface

mongo_client=MongoDBClient()
persons=mongo_client.get_crawled_person(0,100)
personss=['1']
with open('test_data3.txt','w+') as w:
    for id in personss:
        p=mongo_client.get_crawled_person_by_pid("5b642f64a4af2607336f7e40")
        if 'info' in p and p['info'] !="":
            w.write(id)
            w.write('\r\n')
            PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ=interface(p['info'])
            # w.write('PER:'+''.join(PER))
            # w.write('\r\n')
            # w.write('ADR:'+''.join(ADR))
            # w.write('\r\n')
            w.write('AFF:'+''.join(AFF))
            w.write('\r\n')
            w.write('title:'+''.join(TIT))
            w.write('\r\n')
            w.write('job:'+''.join(JOB))
            w.write('\r\n')
            w.write('dom:'+''.join(DOM))
            w.write('\r\n')
            w.write('edu:'+''.join(EDU))
            w.write('\r\n')
            w.write('wrk:'+''.join(WRK))
            w.write('\r\n')
            w.write('soc'+''.join(SOC))
            w.write('\r\n')
            w.write('awd'+''.join(AWD))
            w.write('\r\n')
            w.write('pat'+''.join(PAT))
            w.write('\r\n')
            w.write('prj'+''.join(PRJ))
            w.write('\r\n')
            w.write('######')




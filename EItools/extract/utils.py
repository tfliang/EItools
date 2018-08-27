import logging, sys, argparse


def str2bool(v):
    # copy from StackOverflow
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_entity(tag_seq, char_seq):
    PER = get_PER_entity(tag_seq, char_seq)
    ADR = get_ADR_entity(tag_seq, char_seq)
    AFF = get_AFF_entity(tag_seq, char_seq)
    TIT = get_TIT_entity(tag_seq, char_seq)
    JOB = get_JOB_entity(tag_seq, char_seq)
    # PER = get_name_entitry('PER', tag_seq, char_seq)
    # ADR = get_name_entitry('ADR', tag_seq, char_seq)
    # AFF = get_name_entitry('AFF', tag_seq, char_seq)
    # TIT = get_name_entitry('TIT', tag_seq, char_seq)
    # JOB = get_name_entitry('JOB', tag_seq, char_seq)
    # DOM = get_name_entitry('DOM', tag_seq, char_seq)
    # EDU = get_name_entitry('EDU', tag_seq, char_seq)
    # WRK = get_name_entitry('WRK', tag_seq, char_seq)
    # SOC = get_name_entitry('SOC', tag_seq, char_seq)
    # AWD = get_name_entitry('AWD', tag_seq, char_seq)
    # PAT = get_name_entitry('PAT', tag_seq, char_seq)
    # PRJ = get_name_entitry('PRJ', tag_seq, char_seq)
    # return PER, ADR, AFF, TIT, JOB, DOM, EDU, WRK, SOC, AWD, PAT, PRJ
    return PER, ADR, AFF, TIT, JOB#, DOM, EDU, WRK, SOC, AWD, PAT, PRJ

def get_name_entitry(name, tag_seq, char_seq):
    length = len(char_seq)
    lst = []
    item = ''
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-'+name:
            if len(item) > 0:
                lst.append(item)
            item = char
            if i+1 == length:
                lst.append(item)
        if tag == 'I-'+name:
            item += char
            if i+1 == length:
                lst.append(item)
        if tag not in ['I-'+name, 'B-'+name]:
            if len(item) > 0:
                lst.append(item)
                item = ''
            continue
    return lst

def get_PER_entity(tag_seq, char_seq):
    length = len(char_seq)
    PER = []
    per = ''
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-PER':
            if len(per) > 0:
                PER.append(per)
            per = char
            if i+1 == length:
                PER.append(per)
        if tag == 'I-PER':
            per += char
            if i+1 == length:
                PER.append(per)
        if tag not in ['I-PER', 'B-PER']:
            if len(per) > 0:
                PER.append(per)
                per = ''
            continue
    return PER


def get_ADR_entity(tag_seq, char_seq):
    length = len(char_seq)
    ADR = []
    adr = ''
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-ADR':
            if len(adr) > 0:
                ADR.append(adr)
            adr = char
            if i+1 == length:
                ADR.append(adr)
        if tag == 'I-ADR':
            adr += char
            if i+1 == length:
                ADR.append(adr)
        if tag not in ['I-ADR', 'B-ADR']:
            if len(adr) > 0:
                ADR.append(adr)
                adr = ''
            continue
    return ADR


def get_AFF_entity(tag_seq, char_seq):
    length = len(char_seq)
    AFF = []
    aff = ''
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-AFF':
            if len(aff) > 0:
            # if 'aff' in locals().keys():
                AFF.append(aff)
                # del aff
            aff = char
            if i+1 == length:
                AFF.append(aff)
        if tag == 'I-AFF':
            aff = aff
            aff += char
            if i+1 == length:
                AFF.append(aff)
        if tag not in ['I-AFF', 'B-AFF']:
            if len(aff) > 0:
            # if 'aff' in locals().keys():
                AFF.append(aff)
                # del aff
                aff = ''
            continue
    return AFF

def get_JOB_entity(tag_seq, char_seq):
    length = len(char_seq)
    JOB = []
    job = ''
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-JOB':
            if len(job) > 0:
                JOB.append(job)
            job = char
            if i+1 == length:
                JOB.append(job)
        if tag == 'I-JOB':
            job += char
            if i+1 == length:
                JOB.append(job)
        if tag not in ['I-JOB', 'B-JOB']:
            if len(job) > 0:
                JOB.append(job)
                job = ''
            continue
    return JOB

def get_TIT_entity(tag_seq, char_seq):
    length = len(char_seq)
    TIT = []
    tit = ''
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-TIT':
            if len(tit) > 0:
                TIT.append(tit)
            tit = char
            if i+1 == length:
                TIT.append(tit)
        if tag == 'I-TIT':
            tit += char
            if i+1 == length:
                TIT.append(tit)
        if tag not in ['I-TIT', 'B-TIT']:
            if len(tit) > 0:
                TIT.append(tit)
                tit = ''
            continue
    return TIT


def get_logger(filename):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)
    return logger

import os
from logging import Logger
from os.path import join,exists,dirname


def mkdir(dirpath):
    if not exists(dirpath):
        os.mkdir(dirpath)

DIR_SRC=dirname(__file__)
DIR_PRJ=dirname(DIR_SRC)

DIR_MOD=join(DIR_PRJ,'classifier_email')
DIR_CONFIG=join(DIR_PRJ,'config')
DIR_CACHE=join(DIR_PRJ,'cache')
FILE_SVM_MOD=join(DIR_MOD,'svm-model.pkl')

FILE_CONFIG=join(DIR_CONFIG,'crawlers.json')
DATA_DICT=join(DIR_CONFIG,'data_dict.json')

CLASSIFIER_DIR=join(DIR_PRJ,'classifier_mainpage')
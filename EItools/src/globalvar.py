import os
from logging import Logger
from os.path import join,exists,dirname


def mkdir(dirpath):
    if not exists(dirpath):
        os.mkdir(dirpath)

DIR_SRC=dirname(__file__)
DIR_PRJ=dirname(DIR_SRC)

DIR_DAT=join(DIR_PRJ,'data')
DIR_MOD=join(DIR_DAT,'classifier')
DIR_CONFIG=join(DIR_PRJ,'config')
DIR_CACHE=join(DIR_PRJ,'cache')
FILE_SVM_MOD=join(DIR_MOD,'svm-model.pkl')

FILE_CONFIG=join(DIR_CONFIG,'crawlers.json')

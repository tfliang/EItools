import os
from mongoengine import connection
from os.path import abspath, dirname



MONGO_HOST_PROD = '35.161.192.240'
MONGO_PORT_PROD = 30027
MONGO_USERNAME_PROD = 'kegger_aminer'
MONGO_PASSWORD_PROD = 'jingjieweiwu2016'
MONGO_DBNAME_PROD = 'aminer'



MONGO_HOST = os.environ.get('MONGO_HOST', '166.111.7.173')
MONGO_PORT = os.environ.get('MONGO_PORT', 30019)
MONGO_USERNAME = os.environ.get('MONGO_USERNAME', 'kegger_bigsci')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', 'datiantian123!@#')
MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'bigsci')
MONGO_CRAWLED_PERSON="crawled_person_final"
MONGO_UNCRAWLED_PERSON="uncrawled_person"
MONGO_ALL_TASK="task"

# MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
# MONGO_PORT = os.environ.get('MONGO_PORT', 27017)
# MONGO_USERNAME = os.environ.get('MONGO_USERNAME', '')
# MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', '')

PROD_DB = "aminer"
DEV_DB = "bigsci"
INNER_DB = "inner"

DEFAULT_DB = DEV_DB

connection.register_connection(PROD_DB, name='aminer', host='35.161.192.240', port=30027, username='kegger_aminer', password='jingjieweiwu2016', authentication_mechanism='SCRAM-SHA-1')
connection.register_connection(DEV_DB, name='bigsci', host='166.111.7.173', port=30019, username='kegger_bigsci', password='datiantian123!@#')
connection.register_connection(INNER_DB, name="aminer", host='172.22.245.147', port=27017, username='kegger_aminer', password='jingjieweiwu2016', authentication_mechanism='SCRAM-SHA-1')

PROJ_DIR = abspath(dirname(__file__))

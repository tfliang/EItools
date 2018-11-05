from mongoengine import *
from EItools.client.settings import MONGO_HOST,MONGO_PORT,MONGO_DBNAME,MONGO_PASSWORD,MONGO_USERNAME



# def co():
#     connect(db=DB, host=HOST, port=PORT)
connect(db=MONGO_DBNAME, host=MONGO_HOST, port=MONGO_PORT,username=MONGO_USERNAME,password=MONGO_PASSWORD)

if __name__ == '__main__':
    pass

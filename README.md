#运行环境
python3.6.5  redis-4.0.9 celery-4.2.0 tensorflow
#运行命令
1.运行django server :python3 manage.py runserver ip:port
2.运行celery worker的定时任务进行抓取 celery -A crawl_information worker -B


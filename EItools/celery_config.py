from __future__ import absolute_import, unicode_literals

import os


# set the default Django settings module for the 'celery' program.
from datetime import timedelta

from celery import Celery
from kombu import Queue, Exchange

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EItools.settings')

app = Celery('EItools',
             broker='redis://127.0.0.1:6379/0',
             backend='redis://127.0.0.1:6379/1')


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_queues=(
    Queue('person',routing_key='crawl.person.#'),
    Queue('task',routing_key='crawl.task.#')
)
app.conf.task_routes={
    'EItools.crawler.crawl_information.publish_task':{
        'queue':'task',
        'routing_key':'crawl.task.publish',
    },
    'EItools.crawler.crawl_service.crawl_person_info':{
        'queue':'person',
        'routing_key':'crawl.person.info'
    }
}
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.conf.beat_schedule={
    'publish_task':{
        'task':'EItools.crawler.crawl_information.publish_task',
        'schedule':timedelta(seconds=20),
    },
    'clean_task':{
        'task':'EItools.crawler.crawl_information.clean_task',
        'schedule':timedelta(minutes=20),
        'args':()
    },

}

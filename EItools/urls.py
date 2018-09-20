"""EItools URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from EItools import  settings
from EItools.crawler import crawl_information, task

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^download/crawldata/(.+)/$', task.export_data, name="download"),
    url(r'^view/task/(.+)/',task.get_task_by_id),

    url(r'^upload/crawlfile/$', crawl_information.crawl_file_info),

    url(r'^crawl/person/info/$',crawl_information.crawl_person_by_name),
    url(r'^view/crawldetail/(.+)/(.+)/(.+)/$',crawl_information.get_crawled_persons_by_taskId),
    url(r'^update/persondetail/$',crawl_information.update_person_by_Id),
    url(r'^update/personfield/$',crawl_information.update_person_by_field),
    url(r'^view/persondetail/(.+)/$',crawl_information.get_crawled_persons_by_personId),

    url(r'^show/tasks/(.+)/(.+)/', task.get_tasks_by_page),
    url(r'^save/task/$',task.publish_task),
    url(r'^publish/task/$', crawl_information.publish_task),


    url(r'^crawl/person/info/(.+)/$',crawl_information.crawl_person_by_id)
]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
urlpatterns +=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#!/bin/bash
cd ../EItools/crawler/

celery worker -A crawl_information  -B
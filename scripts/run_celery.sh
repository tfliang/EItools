#!/bin/bash
cd ../EItools/crawler/

celery worker -A crawl_information  -B --concurrency=1
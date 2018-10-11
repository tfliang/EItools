#!/bin/bash
cd ../EItools/crawler/

celery -A crawl_information worker -B
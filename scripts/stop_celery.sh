#!/bin/bash
ps auxww | grep 'celery worker -A crawl_information' | awk '{print $2}' | xargs kill -9



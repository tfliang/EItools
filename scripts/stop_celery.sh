#!/bin/bash
ps auxww | grep 'celery -A crawl_information' | awk '{print $2}' | xargs kill -9


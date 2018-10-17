#!/bin/bash
cd ../EItools/crawler/

ps aux | grep 'celery worker -A ' | awk '{print $2}' | xargs kill -9



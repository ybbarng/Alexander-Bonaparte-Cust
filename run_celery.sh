#!/bin/bash

celery -A abcust worker -l info --concurrency=1 --beat

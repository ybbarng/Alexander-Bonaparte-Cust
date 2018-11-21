#!/bin/bash

celery -A abcust worker -Q ble -l info --concurrency=1

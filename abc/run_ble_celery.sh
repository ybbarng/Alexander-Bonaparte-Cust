#!/bin/bash

celery -A abcust worker -n ble_worker@%h -Q ble -l info --concurrency=1

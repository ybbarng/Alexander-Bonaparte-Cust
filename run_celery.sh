#!/bin/bash

celery -A abcust worker -n main_worker@%h -l info --beat

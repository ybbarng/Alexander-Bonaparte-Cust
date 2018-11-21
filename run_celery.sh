#!/bin/bash

celery -A abcust worker -l info --beat

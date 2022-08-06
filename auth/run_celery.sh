#!/bin/bash

celery -A auth worker -n auth_worker@%h -l info

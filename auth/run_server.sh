#!/bin/bash

export FLASK_APP=auth
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8000

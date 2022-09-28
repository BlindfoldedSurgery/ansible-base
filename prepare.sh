#!/bin/bash

pip3 install virtualenv
python -m virtualenv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

ansible-galaxy install -r requirements.yml

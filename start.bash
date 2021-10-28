#!/bin/bash

source venv/bin/activate
git pull
pip install -r requirements.txt
python app.py

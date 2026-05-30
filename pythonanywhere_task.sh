#!/bin/bash
# ==========================================
# PythonAnywhere Scheduled Task Script
# ==========================================

# 1. Navigate to your project directory. 
# REPLACE 'yourusername' with your actual PythonAnywhere username
# REPLACE 'flask-trackdesk' with your actual project folder name if different
cd /home/bytecore/flask-trackdesk

# 2. Activate your virtual environment
# If you are using a virtualenvwrapper on PythonAnywhere, it might look like:
# source /home/yourusername/.virtualenvs/myenv/bin/activate
# If the venv is inside the project folder, it looks like this:
source /home/bytecore/.virtualenvs/venv/bin/activate

# 3. Export FLASK_APP if necessary (usually 'app.py' or 'app')
# export FLASK_APP=app.py

# 4. Run the Flask CLI command
flask update-expired-documents

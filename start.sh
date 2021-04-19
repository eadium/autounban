#!/bin/bash
screen -dmS autounban python3 autounban/manage.py runserver --insecure 0.0.0.0:5000

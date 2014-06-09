#!/bin/sh
python manage.py sqlclear nf_server | sqlite3 db.sqlite3
python manage.py sql nf_server | sqlite3 db.sqlite3
# python manage.py loaddata dummy2.yaml
python manage.py syncdb
python manage.py loaddata dummy4.yaml

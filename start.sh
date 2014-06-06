#!/bin/sh

# To run this:
# 	chmod u+x start.sh
# 	./start.sh

python manage.py sqlclear nf_server | sqlite3 db.sqlite3
python manage.py sql nf_server | sqlite3 db.sqlite3
python manage.py syncdb
python load_sources.py
python manage.py loaddata dummy3.yaml
COUNTER=0
while true; do
	python scrape.py
	echo Iteration: $COUNTER
	let COUNTER=COUNTER+1 
done
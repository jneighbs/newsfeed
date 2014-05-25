#!/bin/sh

# To run this:
# 	chmod u+x start.sh
# 	./start.sh

python load_sources.py

COUNTER=0
while true; do
	python scrape.py
	echo Iteration: $COUNTER
	let COUNTER=COUNTER+1 
done
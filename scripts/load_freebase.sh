#!/bin/bash

SCRIPT_DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG="freebase.log"

echo "`date` Loading Freebase."
curl -s http://commondatastorage.googleapis.com/freebase-public/rdf/freebase-rdf-latest.gz | gzip -dcf | grep "http://www.w3.org/2000/01/rdf-schema#label" | sort -u -S 1G - |python2.7 "$SCRIPT_DIR/loader.py" &>> "$LOG"
echo "`date` Complete."

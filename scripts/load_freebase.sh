#!/bin/bash

SCRIPT_DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG="freebase.log"

echo "`date` Loading Freebase."
curl -s http://commondatastorage.googleapis.com/freebase-public/rdf/freebase-rdf-latest.gz 2>> "$LOG" | gzip -dcf  2>> "$LOG" | grep "http://www.w3.org/2000/01/rdf-schema#label" | grep "\"@en\s*[.]\s*$" | python2.7 "$SCRIPT_DIR/loader.py" &>> "$LOG"
echo "`date` Complete."

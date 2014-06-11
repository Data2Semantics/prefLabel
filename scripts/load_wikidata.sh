#!/bin/bash

TTL_GZ_FILE="$1"
SCRIPT_DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG="wikidata.log"

echo "`date` Loading $TTL_GZ_FILE."
gunzip --stdout "$TTL_GZ_FILE" 2>> "$LOG" | rapper -i turtle -o ntriples - http://example.com 2>> "$LOG" | grep "http://www.w3.org/2000/01/rdf-schema#label" 2>> "$LOG" | grep "\"@en\s*[.]\s*$" 2>> "$LOG" | python2.7 "$SCRIPT_DIR/loader.py" &>> "$LOG"
echo "`date` Complete."

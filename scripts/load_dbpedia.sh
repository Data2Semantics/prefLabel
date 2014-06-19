#!/bin/bash

NT_BZ2_FILE="~/data/dbpedia/labels_en.nt.bz2"
SCRIPT_DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG="dbpedia.log"

echo "`date` Loading $NT_BZ2_FILE."
bzcat $NT_BZ2_FILE 2>> "$LOG" | grep "http://www.w3.org/2000/01/rdf-schema#label" 2>> "$LOG" | grep "\"@en\s*[.]\s*$" 2>> "$LOG" | python2.7 "$SCRIPT_DIR/loader.py" &>> "$LOG"
echo "`date` Complete."


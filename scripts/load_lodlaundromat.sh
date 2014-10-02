#!/bin/bash

SCRIPT_DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG="lodlaundromat.log"
DOWNLOAD_URL="http://download.lodlaundromat.org"
echo "`date` Loading LOD Laundromat."
echo ">> fetching dataset references"

# get all the hashes we can use. Prune by filtering datasets without literals
hashes=`curl -s 'http://sparql.backend.lodlaundromat.org/?query=PREFIX+llo%3A+%3Chttp%3A%2F%2Flodlaundromat.org%2Fontology%2F%3E%0APREFIX+llm%3A+%3Chttp%3A%2F%2Flodlaundromat.org%2Fmetrics%2Fontology%2F%3E%0APREFIX+ll%3A+%3Chttp%3A%2F%2Flodlaundromat.org%2Fresource%2F%3E%0ASELECT+%3Fmd5+%7B%0A++%5B%5D+llo%3Amd5+%3Fmd5+%3B%0A++++llm%3Ametrics%2Fllm%3AdistinctLiterals+%3FnumLiterals.%0A++FILTER(%3FnumLiterals+%3E+0)%0A%7D' -H 'Accept: text/csv'`
while read -r line; do
    #remove quotes:
    unquoted=${line:1:${#line}-2}
    if [[ ${#unquoted} -eq 32 ]]; then
	#validate string length. this way, we exclude e.g. the variable name at the first row as well
	curl -s $DOWNLOAD_URL/$unquoted | gzip -dcf | grep "http://www.w3.org/2000/01/rdf-schema#label" | sort -u -S 1G - | python2.7 "$SCRIPT_DIR/loader.py" & >> "$LOG";
    fi
done <<EOF
< "$hashes"
EOF

echo "`date` Complete."

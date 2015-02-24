#!/bin/bash


lim=100
off=0


DOWNLOAD_URL="http://download.lodlaundromat.org"
SCRIPT_DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG="lodlaundromat.log"
echo "`date` Loading LOD Laundromat."
echo ">> fetching dataset references"


while true; do
  # get all the hashes we can use. Prune by filtering datasets without literals
  #hashes=`curl -s 'http://sparql.backend.lodlaundromat.org/?query=PREFIX+llo%3A+%3Chttp%3A%2F%2Flodlaundromat.org%2Fontology%2F%3E%0APREFIX+llm%3A+%3Chttp%3A%2F%2Flodlaundromat.org%2Fmetrics%2Fontology%2F%3E%0APREFIX+ll%3A+%3Chttp%3A%2F%2Flodlaundromat.org%2Fresource%2F%3E%0ASELECT+%3Fmd5+%7B%0A++%5B%5D+llo%3Amd5+%3Fmd5+%3B%0A++++llm%3Ametrics%2Fllm%3AdistinctLiterals+%3FnumLiterals.%0A++FILTER(%3FnumLiterals+%3E+0)%0A%7D' -H 'Accept: text/csv'`
  hashes=`curl -s "http://lodlaundromat.org/sparql/?query=PREFIX%20llo%3A%20%3Chttp%3A%2F%2Flodlaundromat.org%2Fontology%2F%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0A%0ASELECT%20DISTINCT%20%3Fmd5%20WHERE%20%7B%0A%20%20%5B%5D%20llo%3Atriples%20%3Ftriples%20%3B%0A%20%20%20%20llo%3Amd5%20%3Fmd5%20.%0A%20%20FILTER(%3Ftriples%20%3E%200)%0A%7D%20LIMIT+$lim+OFFSET+$off"  -H 'Accept: text/csv' | sed '1d' | sed 's/\"//g'`
  readCount=0;
  while read -r line; do
    if [[ ${#line} -eq 32 ]]; then
      readCount=`expr $readCount + 1`;
      curl -s $DOWNLOAD_URL/$line | gzip -dcf | grep "http://www.w3.org/2000/01/rdf-schema#label" | uniq | python2.7 "$SCRIPT_DIR/loader.py" & >> "$LOG";
    fi
  done <<EOF
  < "$hashes"
EOF

  if [ "$readCount" -eq "0" ]; then
    echo "`date` Complete."
    exit 0;
  else 
    echo "Read $readCount hashes"
  fi
  off=`expr $off + $lim`
done




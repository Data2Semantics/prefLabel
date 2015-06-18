#!/bin/bash
curl -X GET -s "http://lov.okfn.org/lov.nq.gz" | gzip -dcf | grep "http://www.w3.org/2000/01/rdf-schema#label" | rapper -i nquads -o ntriples -I example.com - | sort -u - | bzip2 > sorted_lov-`date "+%Y-%m-%d"`.nt.bz2

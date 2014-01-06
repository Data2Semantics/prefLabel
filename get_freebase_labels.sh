#!/bin/bash
curl http://commondatastorage.googleapis.com/freebase-public/rdf/freebase-rdf-2013-12-22-00-00.gz | gzip -dcf | grep "http://www.w3.org/2000/01/rdf-schema#label" | grep "\"@en\b"

#!/bin/bash
curl -Ls http://download.freebaseapps.com | gzip -dcf | grep "http://www.w3.org/2000/01/rdf-schema#label" | grep "\"@en\s*[.]\s*$"

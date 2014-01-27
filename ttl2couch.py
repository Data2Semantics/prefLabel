#!/usr/bin/env python2.7

import sys
import urllib
import rdflib
import couchdbkit
import restkit
from couchdbkit.designer import push
from time import time
from glob import glob
import datetime

dbname = sys.argv[1]
# dbname = 'preflabel'
fnames = sys.argv[2:]
# fname = './test/labels1000.ttl'
# fnames = [fname]

rdfslabel = "http://www.w3.org/2000/01/rdf-schema#label"
server = couchdbkit.Server(filters=[restkit.BasicAuth('admin', 'admin')])
# try:
#     server.delete_db(dbname)
# except:
#     pass

db = server.get_or_create_db(dbname)

for fname in fnames:
    try:
        g = rdflib.Graph()
        print "{} {} Parsing TTL".format(datetime.datetime.utcnow(), fname)
        g.parse(fname, format='turtle')
        print "{} {} Preparing docs".format(datetime.datetime.utcnow(), fname)
        docs = [{"_id": s, "l": unicode(o)} for s, p, o in g]

        print "{} {} Saving docs".format(datetime.datetime.utcnow(), fname)
        db.save_docs(docs)
    except Exception as e:
        print "Unexpected error: {}".format(sys.exc_info()[0])

push('./index', db)

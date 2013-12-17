# splitaaaaq - fail

import itertools
import sys
import rdflib
import couchdbkit
import restkit
from couchdbkit.designer import push
from time import time
from glob import glob
dbname = 'r4'
fnames = glob('./data/split*')
fname = './data/labels1000.ttl'
# fname = './dbpedia3.9_labels_en.ttl'
fnames = [fname]

rdfslabel = "http://www.w3.org/2000/01/rdf-schema#label"
server = couchdbkit.Server(filters=[restkit.BasicAuth('admin', 'admin')])
try:
    server.delete_db(dbname)
except:
    pass

db = server.get_or_create_db(dbname)

for fname in fnames:
    try:
        g = rdflib.Graph()
        print "{} Parsing TTL".format(fname)
        g.parse(fname, format='turtle')
        print "{} Preparing docs".format(fname)
        docs = [{"_id": s[28:], "@id": unicode(s), "label": unicode(o)} for s, p, o in g]

        print "{} Saving docs".format(fname)
        db.save_docs(docs)
    except Exception as e:
        print "Unexpected error: {}".format(sys.exc_info()[0])

push('./index', db)

#!/usr/bin/env python2.7
import couchdbkit
import restkit
import sys
from couchdbkit.designer import push
if len(sys.argv) == 3:
    username, password = sys.argv[1:3]
    filters = [restkit.BasicAuth(username, password)]
else:
    filters = None
dbname = 'preflabel'
server = couchdbkit.Server(filters=filters)
db = server.get_or_create_db(dbname)
push('./_design/index', db)

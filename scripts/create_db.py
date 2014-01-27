#!/usr/bin/env python2.7
import couchdbkit
from couchdbkit.designer import push
dbname = 'preflabel'
server = couchdbkit.Server()
db = server.get_or_create_db(dbname)
push('./index', db)

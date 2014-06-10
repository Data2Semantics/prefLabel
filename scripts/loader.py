#!/usr/bin/env python2.7

import datetime
import sys
import itertools
import fileinput
import json
import logging
import threading
import Queue
import rdflib
import couchdbkit

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
chunksize = 5000
num_worker_threads = 4

rdfslabel = rdflib.namespace.RDFS['label']
dbname = 'preflabel'
q = Queue.Queue(maxsize=2*num_worker_threads)
server = couchdbkit.Server()
db = server.get_db(dbname)

logging.info("Start loading into '{}'".format(dbname))
logging.debug("Loader params: num_worker_threads={}, chunksize={}".format(num_worker_threads, chunksize))

def nt_fragments():
    chunk = []
    for line in fileinput.input():
        if len(chunk) < chunksize:
            chunk.append(line)
        else:
            yield ''.join(chunk)
            chunk = []
    yield ''.join(chunk)

def jsonify(ntriples):
    g = rdflib.Graph()
    g.parse(data=ntriples, format='nt')
    
    return [{"_id": s, (o.language or 'en') : unicode(o)} 
                for s, o in g.subject_objects(predicate=rdfslabel)]

def worker():
    while True:
        fragment, fragment_number = q.get()
        try:
            db.save_docs(jsonify(fragment), all_or_nothing=True)
        except Exception, e:
            logging.error("While processing fragment #{}: {}".format(fragment_number, e))
        q.task_done()

def start_workers():
    for i in range(num_worker_threads):
         t = threading.Thread(target=worker)
         t.daemon = True
         t.start()

def main():
    start_workers()
    count = itertools.count()
    time_started = rdflib.Literal(datetime.datetime.utcnow())
    command_line = sys.argv[0]
    logging.info("Start time: {}".format(time_started))
    logging.info("Command line: {}".format(command_line))
    for fragment in nt_fragments():
        q.put([fragment, count.next()])
    q.join()
    time_ended = rdflib.Literal(datetime.datetime.utcnow())
    logging.info("End time: {}".format(time_ended))
    logging.info("Loading complete")

if __name__ == '__main__':
    main()

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
min_chunk_size = 5000
num_worker_threads = 4

DEFAULT_LANGUAGE = 'en'
rdfslabel = rdflib.namespace.RDFS['label']
dbname = 'preflabel'
q = Queue.Queue(maxsize=2*num_worker_threads)
server = couchdbkit.Server()
db = server.get_db(dbname)

def nt_subj(nt_line):
    tokens = nt_line.split()
    if (len(tokens) > 2) and (tokens[0][0] == '<'):
        return tokens[0]
    else:
        return None

def nt_fragments(input_lines=fileinput.input()):
    chunk = []
    last_subj = None
    for line in input_lines:
        if last_subj:
            if nt_subj(line) != last_subj:
                yield (''.join(chunk)).strip()
                chunk = []
                last_subj = None
        elif len(chunk) > min_chunk_size - 2:
            last_subj = nt_subj(line)
        chunk.append(line)
    yield (''.join(chunk)).strip()

def jsonify(ntriples):
    g = rdflib.Graph()
    g.parse(data=ntriples, format='nt')
    docs = []
    for s in g.subjects():
        doc = {"_id": s}
        for o in g.objects(subject=s, predicate=rdfslabel):
            doc[o.language or DEFAULT_LANGUAGE] = unicode(o)
        docs.append(doc)
    return docs

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
    logging.info("Start loading into '{}'".format(dbname))
    logging.debug("Loader params: num_worker_threads={}, min_chunk_size={}".format(num_worker_threads, min_chunk_size))
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

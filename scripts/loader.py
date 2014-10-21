#!/usr/bin/env python2.7

import datetime
import optparse
import fileinput
import logging
import threading
import Queue
import couchdbkit
import rdflib
from rdflib.namespace import RDFS, OWL

min_chunk_size = 5000
DEFAULT_DB = 'http://localhost:5984/preflabel'
DEFAULT_WORKER_THREADS = 4
DEFAULT_LANGUAGE = 'en'
prov_url = ''
db = None
q = None


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
    # rdflib N-Triples parser does not support utf-8 strings yet, using 'turtle' helps.
    g.parse(data=ntriples, format='turtle')
    docs = []
    for s in set(g.subjects()):
        doc = {"_id": s}
        labels = {
            o.language or DEFAULT_LANGUAGE: unicode(o)
            for o in g.objects(subject=s, predicate=RDFS['label'])
            if isinstance(o, rdflib.Literal)}
        if labels:
            doc["labels"] = labels
            doc["prov"] = prov_url
            sameAs = list(g.objects(subject=s, predicate=OWL['sameAs']))
            if sameAs:
                doc["sameAs"] = sameAs
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


def start_workers(num_worker_threads):
    for i in range(num_worker_threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()


def load_nt(files, num_worker_threads=DEFAULT_WORKER_THREADS):
    global q
    q = Queue.Queue(maxsize=num_worker_threads*2)
    logging.debug("Loader params: num_worker_threads={}, min_chunk_size={}".format(
        num_worker_threads, min_chunk_size))
    start_workers(num_worker_threads)
    for fragment_number, fragment in enumerate(nt_fragments(fileinput.input(files))):
        q.put([fragment, fragment_number])
    q.join()


def main():
    global db
    global prov_url
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
    parser = optparse.OptionParser()
    parser.add_option(
        '-t', '--target_db',
        help="Target database URL. Default is {}.".format(DEFAULT_DB),
        default=DEFAULT_DB)
    parser.add_option(
        '-n', '--num_worker_threads',
        help="Number of worker threads. Default is {}.".format(DEFAULT_WORKER_THREADS),
        type=int,
        default=DEFAULT_WORKER_THREADS)
    parser.add_option(
        '-p', '--provenance_url',
        help='Provenance URL.',
        default='')
    options, files = parser.parse_args()
    db = couchdbkit.Database(options.target_db)
    prov_url = options.provenance_url

    logging.info("Start loading into '{}'".format(db.uri))
    time_started = rdflib.Literal(datetime.datetime.utcnow())
    logging.info("Start time: {}".format(time_started))
    load_nt(files, num_worker_threads=options.num_worker_threads)
    time_ended = rdflib.Literal(datetime.datetime.utcnow())
    logging.info("End time: {}".format(time_ended))
    logging.info("Loading complete")

if __name__ == '__main__':
    main()

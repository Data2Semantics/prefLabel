#!/usr/bin/env python2.7

import datetime
import optparse
import fileinput
import logging
import multiprocessing
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


def nt_fragments(input_lines):
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


def uri_filter(term):
    return isinstance(term, rdflib.URIRef)


def domain_filter(url, domain):
    """Return True if the second level domani of the url matches domain"""
    term_domain = '.'.join(url.split('/')[2] .split('.')[-2:])
    return term_domain == domain


def jsonify(ntriples, subject_filter=uri_filter):
    g = rdflib.Graph()
    # rdflib N-Triples parser does not support utf-8 strings yet, using 'turtle' helps.
    g.parse(data=ntriples, format='turtle')
    docs = []
    subjects = {s for s in g.subjects() if subject_filter(s)}
    for s in subjects:
        doc = {"_id": s}
        labels = {
            o.language or DEFAULT_LANGUAGE: unicode(o)
            for o in g.objects(subject=s, predicate=RDFS['label'])
            if isinstance(o, rdflib.Literal)}
        if labels:
            doc["labels"] = labels
            doc["prov"] = prov_url
            same_as = list(g.objects(subject=s, predicate=OWL['sameAs']))
            if same_as:
                doc["sameAs"] = same_as
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
        t = multiprocessing.Process(target=worker)
        t.daemon = True
        t.start()


def load_nt(files, num_worker_threads=DEFAULT_WORKER_THREADS):
    global q
    q = multiprocessing.JoinableQueue(maxsize=num_worker_threads * 4)
    logging.debug("Using num_worker_threads={}, min_chunk_size={}".format(
        num_worker_threads, min_chunk_size))
    start_workers(num_worker_threads)
    chunked_input = nt_fragments(fileinput.input(files, bufsize=2048 * 1024))
    for fragment_number, fragment in enumerate(chunked_input):
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

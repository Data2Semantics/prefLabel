import itertools
import fileinput
import json
import logging
import threading
import Queue
import rdflib
import couchdbkit

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
chunksize = 2000
num_worker_threads = 20

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
    return [{"_id": s, "l": unicode(o)} for s, o in g.subject_objects(predicate=rdfslabel)]

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
    for fragment in nt_fragments():
        q.put([fragment, count.next()])
    q.join()
    logging.info("Loading complete")

if __name__ == '__main__':
    main()

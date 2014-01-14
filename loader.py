import fileinput
import Queue
import threading
import rdflib
import couchdbkit
import json

chunksize = 5000
num_writer_threads = 2
rdfslabel = rdflib.namespace.RDFS['label']
dbname = 'preflabel'

server = couchdbkit.Server()
db = server.get_db(dbname)

def chunks():
    chunk = []
    for line in fileinput.input():
        if len(chunk) < chunksize:
            chunk.append(line)
        else:
            yield ''.join(chunk)
            chunk = []
    yield ''.join(chunk)

def chunk2doc(chunk):
    g = rdflib.Graph()
    g.parse(data=chunk, format='nt')
    return [{"_id": s, "l": unicode(o)} for s, o in g.subject_objects(predicate=rdfslabel)]


def writer():
    while True:
        update = q.get()
        try:
            db.save_docs(update, all_or_nothing=True)
        except:
            json.dump(update, fout, indent=2)
            fout.write(',\n')
        q.task_done()

q = Queue.Queue()
for i in range(num_writer_threads):
     t = threading.Thread(target=worker)
     t.daemon = True
     t.start()

updates = (chunk2doc(c) for c in chunks())
fout = open('failed_updates.json', 'w')
fout.write('[')

for update in updates:
    q.put(update)

q.join()       # block until all tasks are done

fout.write('{}]')
fout.close()

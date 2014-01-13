import fileinput
import rdflib
import couchdbkit
import json

chunksize = 5000
rdfslabel = rdflib.namespace.RDFS['label']
dbname = 'study'

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

updates = (chunk2doc(c) for c in chunks())

fout = open('failed_updates.json', 'w')
fout.write('[')
for update in updates:
    try:
        db.save_docs(update, all_or_nothing=True)
    except:
        json.dump(update, fout, indent=2)
fout.write(']')
fout.close()

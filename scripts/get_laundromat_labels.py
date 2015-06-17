import itertools
import requests
import threading
import Queue
import urllib2
import zlib
from SPARQLWrapper import SPARQLWrapper

RDFS_LABEL = 'http://www.w3.org/2000/01/rdf-schema#label'
EXCLUDED_DOMAINS = set([
    'geonames.org',
    'dbpedia.org',
    'freebase.com',
    'wikidata.org'])

num_worker_threads = 4
target_dir = 'laundromat_labels'
queue = Queue.Queue()


def lld_datasets(resource):
    """
    Find LOD Laundromat documents mentioning resource
    """
    url = 'http://index.lodlaundromat.org/r2d/?limit=1000000&uri={}'.format(
        urllib2.quote(resource, safe=''))
    return set(requests.get(url).json()['results'])


def sparql_query(endpoint, query, page_size=10000):
    """
    Paginate query and return a generator over depaginated results.
    """
    q = lambda page: '{}\noffset {}\nlimit {}'.format(
        query, page * page_size, page_size)
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat('json')
    current_page = 0
    while True:
        sparql.setQuery(q(current_page))
        bindings = sparql.queryAndConvert()['results']['bindings']
        if bindings:
            for b in bindings:
                yield b
        else:
            return
        current_page += 1


second_level_domain = lambda url: '.'.join(
    urllib2.urlparse.urlsplit(url)[1].split('.')[-2:]) or None


def datasets_info():
    query = '''
    PREFIX llo: <http://lodlaundromat.org/ontology/>
    PREFIX ll: <http://lodlaundromat.org/resource/>
    SELECT ?md5 ?downloadURL ?nTriples
    {
    ?maybearchive llo:url ?downloadURL; llo:containsEntry* ?dataset .
    ?dataset llo:md5 ?md5; llo:triples ?nTriples .
    }
    '''
    query_results = sparql_query(
        'http://lodlaundromat.org/sparql/', query, page_size=10000)
    datasets_with_labels = lld_datasets(RDFS_LABEL)
    return ((
        r['md5']['value'],
        r['downloadURL']['value'])
        # second_level_domain(r['downloadURL']['value']),
        for r in query_results
        if r['md5']['value'] in datasets_with_labels)


def save_datasets_info():
    import csv
    csv_writer = csv.writer(open('lld_resources_with_labels.csv', 'w'))
    csv_writer.writerows(datasets_info())


def dataset_triples(md5):
    url = 'http://download.lodlaundromat.org/{}'.format(md5)
    r = requests.get(url, stream=True)
    dec = zlib.decompressobj(32 + zlib.MAX_WBITS)
    pending = ''
    for zip_chunk in r.iter_content():
        if not zip_chunk:
            continue
        chunk = pending + dec.decompress(zip_chunk)
        lines = chunk.splitlines(True)
        if lines and lines[-1] and lines[-1][-1] != '\n':
            pending = lines.pop()
        else:
            pending = ''
        for line in lines:
            yield line
    yield pending


def same_domain_label(line, domain):
    try:
        subj, pred, _ = line.split(None, 2)
    except ValueError:
        return False
    return (
        pred[1:-1] == RDFS_LABEL
        and second_level_domain(subj[1:-1]) == domain)


def save_dataset_labels(md5, allowed_domain):
    labels = (
        line for line in dataset_triples(md5)
        if same_domain_label(line, allowed_domain))
    fname = '{}/{}.nt'.format(target_dir, md5)
    with open(fname, 'w') as f:
        f.writelines(labels)


def worker():
    while True:
        try:
            md5, download_url = queue.get(block=False)
        except Queue.Empty:
            # print "Queue empty, worker is done"
            return
        source_domain = second_level_domain(download_url)
        if source_domain not in EXCLUDED_DOMAINS:
            save_dataset_labels(md5, source_domain)
        # print 'Got {}'.format(md5)
        queue.task_done()


def start_workers():
    for i in range(num_worker_threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()


def main():
    infos = itertools.islice(datasets_info(), 37, 41)
    for info in infos:
        queue.put(info)
    start_workers()
    queue.join()
    print "All done"


if __name__ == '__main__':
    main()

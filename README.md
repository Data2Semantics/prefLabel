prefLabel
=========

This repository contains scripts for http://preflabel.org, a service providing
a simple API for fast RDF entity label lookup.

## Install

#### Prerequisites:

- [CouchDB](http://couchdb.apache.org/#download)
- [Couchapp](https://pypi.python.org/pypi/Couchapp)


#### Install preflabel app:

```
git clone https://github.com/cmarat/prefLabel.git
cd preflabel/preflabel
couchapp push . http://user:pass@localhost:5984/preflabel
```

## Load data

You might need to modify `scripts/loader.py` to load N-Triples files into the database. 

## Use

Application is available at
http://localhost:5984/preflabel/_design/preflabel/_rewrite/

The API endpoint is
http://localhost:5984/preflabel/_design/preflabel/_rewrite/api/v1/

If you use Apache, ProxyPass http://localhost:5984/preflabel/_design/preflabel/_rewrite/ to the root of your server.


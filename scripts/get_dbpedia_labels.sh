wget -rc  --no-parent --accept "*labels_en*.nt.bz2","iri_sameas_uri_*.nt.bz2" http://data.dws.informatik.uni-mannheim.de/dbpedia/2014/
wget -rc  --no-parent --accept "*.nt.bz2" http://data.dws.informatik.uni-mannheim.de/dbpedia/2014/links/
wget -r http://data.dws.informatik.uni-mannheim.de/dbpedia/2014/dbpedia_2014.owl.bz2
wget -r http://data.dws.informatik.uni-mannheim.de/dbpedia/2014/en/geonames_links_en_en.nt.bz2
bzcat `find data.dws.informatik.uni-mannheim.de/ -name "*labels*.nt.bz2"` | grep --color=auto "http://www.w3.org/2000/01/rdf-schema#label" | sort -u -S 10G | bzip2 > sorted_labels.bz2

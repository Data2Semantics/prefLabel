function(doc, req) {
	if (doc['json-ld']) {
		return {'body': JSON.stringify(doc['json-ld'], null, '  '), 'headers': {'Content-Type': 'application/ld+json'}};
	} else {
		return {'code': 404, 'json': {'error':'not_found','reason':'document not found'}}
	}
}

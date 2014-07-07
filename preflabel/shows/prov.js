function(doc, req) {
    var data = (doc || {})['json-ld'];
	if (data) {
		return {'body': JSON.stringify(data, null, '  '), 'headers': {'Content-Type': 'application/ld+json'}};
	} else {
		return {'code': 404, 'json': {'error':'not_found','reason':'document not found'}};
	}
}

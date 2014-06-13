function(doc, req){
  var headers = {};
  if (doc) {
    var prov = ''
    if (doc['prov']) {
      prov = doc['prov'] + '; rel="http://www.w3.org/ns/prov#has_provenance" '
    }
    if (req.headers['Accept'].match(/json/)) {
      return {body: JSON.stringify({'label': doc['en']}),
              headers: {
                'Content-Type': 'application/json',
                'Link' : prov
              }};
    } else {
      return {body: doc['en'],
              headers: {
                'Content-Type': 'text/plain',
                'Link' : prov
              }};
    }
  } else {
    return {
      body: JSON.stringify( {'error': 'not_found', 'reason': 'no data for <' + req.id + '>'}),
      headers: {'Content-Type': 'application/json'},
      code : 404
    };
  };
}

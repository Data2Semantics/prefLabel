function(head, req) {

  function searchLabel (languageList) {
    while(row = getRow()){
      var label = '';
      var lang = '';
      var labels = (row.doc || {}).labels;
      var provLink = '';
      if (labels) {
        for (var i=0; i<languageList.length; i++) {
          lang = languageList[i];
          label = labels[lang];
          if (label) {
            if (row.doc.prov) {
              provLink = "http://preflabel.org/ld/prov/" + row.doc.prov +
                "; rel='http://www.w3.org/ns/prov#has_provenance';" +
                " anchor='http://preflabel.org/ld/dummy" + "'";
            }
            return {'label': label, 'lang': lang, 'prov': provLink};
          }
        }
      }
    }
    return null;
  }

  var langs = [];
  if ('Accept-Language' in req.headers) {
    req.headers['Accept-Language'].toLowerCase().split(',').forEach( function (el, i, array) {
      langs[i] = el.trimLeft().slice(0,2); 
    });
  } else {
    langs[0] = 'en';
  };

  result = searchLabel(langs);
  if (result) {
    if (req.headers['Accept'].match(/json/)) {
      start({'headers': {
        'Content-Type': 'application/json',
        'Content-Language': result.lang,
        'Link': result.prov }});
      send(JSON.stringify({
        'label': result.label,
        'lang': result.lang }));
    } else {
      start({'headers': { 'Content-Type': 'text/plain',
                          'Content-Language': result.lang,
                          'Link': result.prov }});
      send(result.label);
    }
  } else if (req.query.silent) {
    start({'code': 204, 'headers': {'Content-Type': 'application/json'}});
    send(JSON.stringify({'error': 'not_found', 'reason': 'no data for <' + req.query.key + '>'}));
  } else {
    start({'code': 404, 'headers': {'Content-Type': 'application/json'}});
    send(JSON.stringify({'error': 'not_found', 'reason': 'no data for <' + req.query.key + '>'}));
  }
}

function(head, req) {

  function searchLabel (languageList) {
    while(row = getRow()){
      var label = '';
      var lang = '';
      var labels = (row.doc || {}).labels;
      if (labels) {
        for (var i=0; i<languageList.length; i++) {
          lang = languageList[i];
          label = labels[lang];
          if (label) {
            return { 'label': label,
                     'lang': lang,
                     'prov': (row.doc.prov || '') };
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
    var provLink = result.prov + "; rel='http://www.w3.org/ns/prov#has_provenance'";
    if (req.headers['Accept'].match(/json/)) {
      start({'headers': {
        'Content-Type': 'application/json',
        'Content-Language': result.lang,
        'Link': provLink }});
      send(JSON.stringify({
        'label': result.label,
        'lang': result.lang }));
    } else {
      start({'headers': { 'Content-Type': 'text/plain',
                          'Content-Language': result.lang,
                          'Link': provLink }});
      send(result.label);
    }
  } else if (req.query.silent) {
    start({'code': 204});
    send('');
  } else {
    start({'code': 404});
    send('');
  }
}


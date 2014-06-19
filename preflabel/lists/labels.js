function(head, req) { 
  start({'headers': {'Content-Type': 'application/json'}});
  var response = {"results": []};
  while(row = getRow()){
    var o = {};
    if (row.doc) {
      o[row.key] = row.doc.en;
    } else {
      o[row.key] = null
    }
    response.results.push(o)
  }
  send(toJSON(response));
}

function(head, req) { 
  provides('json', function(){
    var response = {"results": []};
    while(row = getRow()){
      var o = {}
      o[row.key] = row.value
      response.results.push(o)
    }
    return(toJSON(response));
  });
  provides('text', function(){
    var results = '';
    while(row = getRow()){
      results += row.value + '\n'
    }
    return(results);
  });
}

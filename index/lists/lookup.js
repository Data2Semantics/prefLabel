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
}

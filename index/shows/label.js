function(doc, req){
  provides('json', function(){
     return toJSON({'label': doc['l']})});
  provides('text', function(){
     return doc['l'] });
}

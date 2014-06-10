function(doc, req){
  var headers = {};
  if (doc) {
    if (req.headers["Accept"].match(/json/)) {
      return {body: JSON.stringify({'label': doc['en']}),
              headers: {"Content-Type": "application/json"}};
    } else {
      return {body: doc['en'],
              headers: {"Content-Type": "text/plain"}};
    }
  } else {
    return {
      body: JSON.stringify( {"error": "not_found", "reason": "no data for <" + req.id + ">"}),
      headers: {"Content-Type": "application/json"},
      code : 404
    };
  };
}

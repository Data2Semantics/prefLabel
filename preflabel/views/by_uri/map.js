function(doc) {
  if (doc.labels) {
    if (doc["_id"].slice(0, 4) === "http") emit(doc["_id"]);
    if (doc.sameAs)
      for (var i=0; i<doc.sameAs.length ; i++) emit(doc.sameAs[i]);
  }
}

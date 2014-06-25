function(doc) {
  if (doc.labels)
    for (var i=0; i<doc.sameas.length ; i++) emit(doc.sameas[i]);
}

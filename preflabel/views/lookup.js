function(doc) {
  languages = ['en', 'fr'];
  for (var i = 0; i < languages.length(); i++) {
    lang = languages[i];
    if (doc[lang]) {
      emit([lang, doc[lang]]);
    }
  }
}

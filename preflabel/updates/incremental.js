function(doc, req){
    var data = JSON.parse(req.body);
    if (doc) {
        doc[data[0]] = data[1];
        return [doc, "entity updated\n"];
    } else if (req.id) {
        doc = {'_id': req.id};
        doc[data[0]] = data[1];
        return [doc, "entity created\n"];
    }
    return [null, "missing document id\n"]
}


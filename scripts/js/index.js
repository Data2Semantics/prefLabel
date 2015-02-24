var request = require('superagent'),
    fs = require('fs'),
    config = require('./config');


var labels = {};
var nextLabelPage;
var getLabelsFromDataset = function(url, callback) {
    nextLabelPage = null;
    request
        .get(url)
        .set('Accept', 'application/json')
        .end(function(error, res){
                
            res.body['@graph'].forEach(function(labelInfo){
                
                if (labelInfo['@id'] === url + '#metadata') {
                    var metadata = labelInfo['@graph'];
                    metadata.forEach(function(md) {
                        if (md['http://www.w3.org/ns/hydra/core#nextPage']) {
                            nextLabelPage = md['http://www.w3.org/ns/hydra/core#nextPage']['@id'];
                        } 
                    });
                } else {
                    var label = labelInfo['http://www.w3.org/2000/01/rdf-schema#label'];
                    if (label) {
                        if (typeof label == "string") {
                            labels[labelInfo['@id']] = label;
                        } else {
                            labels[labelInfo['@id']] = label['@value'];
                        }
                    }
                }
            });
            if (nextLabelPage) {
                getLabelsFromDataset(nextLabelPage, callback);
            } else {
                storeLabels(url, callback);
            }
        })
    
};

var storeLabels = function(url, callback) {
    if (Object.keys(labels).length > 0) {
        console.log("Storing " + Object.keys(labels).length + " labels");
        //write to file, and apply loader
        var tmpFilename = '/tmp/llPreflabels';
        var stream = fs.createWriteStream(tmpFilename);
        stream.once('open', function(fd) {
            for (var obj in labels) {
                stream.write('<' + obj + '> <http://www.w3.org/2000/01/rdf-schema#label> "' + labels[obj] + '" .\n');//write as ntriple (required by loader)
            }
            stream.end();
            //reset labels obj again
            labels = {};
            var exec = require('child_process').exec;
            exec(__dirname + '/../loader.py ' + tmpFilename, function() {
                callback();
            })
        });
    } else {
        console.log("Nothing to store");
        callback();
    }
};
var getLdfLabelUrl = function(md5) {
    return config.ldfUrl + '/' + md5 + '?predicate=' + encodeURIComponent('http://www.w3.org/2000/01/rdf-schema#label'); 
}

var datasetsToProcess = [];
var nextDatasetPage;
var getDatasets = function(ldfUrl, callback) {
    nextDatasetPage = null;
    request
    .get(ldfUrl)
    .set('Accept', 'application/json')
    .end(function(error, res){
        res.body['@graph'].forEach(function(ds){
            if ('http://purl.org/dc/terms/title' in ds) {
                datasetsToProcess.push(ds['http://purl.org/dc/terms/title']);
            } else if (ds['@graph']){
                var metadata = ds['@graph'];
                metadata.forEach(function(md) {
                    if (md['http://www.w3.org/ns/hydra/core#nextPage']) {
                        nextDatasetPage = md['http://www.w3.org/ns/hydra/core#nextPage']['@id'];
                    } 
                });
            }
        });
        callback();
    }); 
}


var processDsQueue = function() {
   var ds = datasetsToProcess.shift();
   if (ds) {
       console.log("Processing dataset " + ds);
       getLabelsFromDataset(getLdfLabelUrl(ds), processDsQueue);
   } else {
       if (nextDatasetPage) {
           getDatasets(nextDatasetPage, processDsQueue);
       } else {
           console.log('done! ');
       }
   }
};


getDatasets(config.ldfUrl, processDsQueue);
//getLabelsFromDataset(getLdfLabelUrl('003b78c9e7d55b51400a60be3e5d9931'), function(){console.log('done')});
function(keys, values, rereduce) {
  log(keys);
  if (rereduce) {
    return sum(values);
  } else {
  	var uniqueKeys = {};
  	var count = 0;
  	keys.forEach(function (key) {
  		if (!uniqueKeys.hasOwnProperty(key[0])){
  			count++;
  			uniqueKeys[key[0]] = true;
  		}
  	});
    return count;
  }
}

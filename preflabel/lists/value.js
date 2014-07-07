function(head, req) { 
  start({'headers': {'Content-Type': 'text/plain'}});
  send((getRow() || {}).value || 0);
}

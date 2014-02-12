// Data
var ws = new WebSocket("ws://localhost:8888/data");
ws.onopen = function() {ws.send('{"Xmin": 840469, "Ymin": 6517283, "Xmax": 841560, "Ymax": 6518436}');};
ws.onmessage = function (evt) {alert(evt.data);};

// Sync
var ws = new WebSocket("ws://localhost:8888/sync");
ws.onopen = function() { alert("open")}
ws.onmessage = function (evt) {alert(evt.data);};

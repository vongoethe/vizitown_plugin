var req = new XMLHttpRequest();
req.open('GET', "http://localhost:8888/init", false); 
req.send(null);
if (req.status != 200) {
    throw "No scene defined";
}

var sceneSettings = JSON.parse(req.responseText);
var scene = new Scene({
    window: window,
    document: document,
    domId: "container",
    extent: {
        minX: parseFloat(sceneSettings.extent.xMin),
        minY: parseFloat(sceneSettings.extent.yMin),
        maxX: parseFloat(sceneSettings.extent.xMax),
        maxY: parseFloat(sceneSettings.extent.yMax),
    },
    hasRaster: sceneSettings.hasRaster,
    url: 'localhost:8888',
    vectors: sceneSettings.vectors,
});

sceneSettings.vectors.forEach(function(vector) {
    var checkbox = document.createElement('input');
    checkbox.setAttribute('type', 'checkbox');
    var entry = document.createElement('li');
    var txt = document.createTextNode(vector.name);
    checkbox.setAttribute('value', vector.uuid);
    entry.appendChild(checkbox);
    entry.appendChild(txt);
    document.getElementById("layer-list").appendChild(entry);
});

var refreshLayers = function() {
    var children = [].slice.call(document.getElementById('layer-list').children);
    children.forEach(function(li) {
        var checkbox = li.children[0];
        if (checkbox.checked) {
	     checkbox.checked = false;
	     scene.refreshLayer(checkbox.value);
        }
    });
};
var changeZoomLevel = function(value) {
    scene.zoom(value);
};
console.log(scene);
scene.render();

var saveParameters = function() {
    scene._camera.fov = document.getElementById('angleInput').value;
    scene._camera.far = document.getElementById('deepInput').value;
    scene._scene.fog.far = document.getElementById('deepInput').value;
};

document.getElementById('angleInput').value = scene._camera.fov;
document.getElementById('deepInput').value = scene._camera.far;
document.getElementById('deepInput').value = scene._scene.fog.far;

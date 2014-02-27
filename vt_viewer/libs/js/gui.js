window.addEventListener("load", function(){
	/**
	var slider = document.getElementById('vertical-slider');
	slider.addEventListener('mousedown', function(event){
		event.stopPropagation();
	}, true);
	slider.addEventListener('mouseup', function(event){
		event.stopPropagation();
	}, true);
	slider.addEventListener('change', function(event){
		changeZoomLevel(this.value);
	}, true);
	**/

	document.addEventListener('mousedown', function(event) {
		if(event.srcElement.tagName === "OL") {
			event.stopPropagation();
		}
		if(event.srcElement.tagName === "LI") {
			event.stopPropagation();
		}
		if(event.srcElement.tagName === "H2") {
			event.stopPropagation();
		}
		if(event.srcElement.tagName === "A") {
			event.stopPropagation();
		}
		if(event.srcElement.tagName === "DIV") {
			event.stopPropagation();
		}
		if(event.srcElement.tagName === "INPUT" && event.srcElement.className != "vertical") {
			event.stopPropagation();
		}
	}, true);
});

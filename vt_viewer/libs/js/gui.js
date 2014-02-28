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
		if(event.target.tagName === "FIELDSET") {
			event.stopPropagation();
		}
		if(event.target.tagName === "OL") {
			event.stopPropagation();
		}
		if(event.target.tagName === "LI") {
			event.stopPropagation();
		}
		if(event.target.tagName === "H2") {
			event.stopPropagation();
		}
		if(event.target.tagName === "A") {
			event.stopPropagation();
		}
		if(event.target.tagName === "DIV") {
			event.stopPropagation();
		}
		if(event.target.tagName === "INPUT" && event.srcElement.className != "vertical") {
			event.stopPropagation();
		}
	}, true);
});

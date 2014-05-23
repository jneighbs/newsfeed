function EventTag(inputId)
{
	this.inputBox = document.getElementById(inputId);
	
	if(!this.inputBox)
	{
		return null;
	}

	var that = this;
	this.inputBox.onkeyup = function(event)
	{
		that.keyupHandler();
	}
}

EventTag.prototype.keyupHandler = function()
{
	var marker = document.getElementById("eventTagMarker");
	if(marker)
	{
		marker.parentElement.removeChild(marker);
	}

	if(this.inputBox.value.length > 0)
	{
		var encQuery = encodeURIComponent(this.inputBox.value);
		Ajaxy.request("/check_event_tag/" + encQuery, "GET", undefined,"", this.ajaxSuccessHandler, null, this);
	}

}

EventTag.prototype.ajaxSuccessHandler = function(responseText)
{
	var marker = document.getElementById("eventTagMarker");
	if(marker)
	{
		marker.parentElement.removeChild(marker);
	}

	var y = this.inputBox.offsetTop;
	var x = this.inputBox.offsetWidth + this.inputBox.offsetLeft;
	var marker = document.createElement("div");
	if(responseText == "0")
	{
		// We're good to go

		marker.innerHTML = "That'll do.";
	}
	else
	{
		// show an error
		marker.innerHTML = "Wah-wuh, already taken.";
	}
	marker.style.left = x + "px";
	marker.style.top = y + "px";
	marker.style.position = "absolute";
	marker.id = "eventTagMarker";
	this.inputBox.parentElement.appendChild(marker);
}
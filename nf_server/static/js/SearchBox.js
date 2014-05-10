function SearchBox(sbId, targetId, models)
{
	this.target = document.getElementById(targetId);

	var searchBox = document.getElementById(sbId);
	if(!searchBox)
	{
		return null;
	}
	var inputs = searchBox.getElementsByTagName("input");
	for(var i = 0; i < inputs.length; i++)
	{
		if(inputs[i].type == "text")
		{
			this.searchField = inputs[i];
		}
	}

	if(this.searchField)
	{
		// attach click handlers
		var obj = this;
		this.searchField.onkeyup = function(event)
		{
			var encQuery = encodeURIComponent(obj.searchField.value);
			encQuery += "?models=" + encodeURIComponent(models);
			console.log("Encoded query:" + encQuery);
			Ajaxy.request("/search/" + encQuery, "GET", undefined,"", obj.ajaxSuccessHandler, null, obj);
		}
	}
	else
	{
		return null;
	}
}

SearchBox.prototype.ajaxSuccessHandler = function(responseText)
{
	/*
	if(responseText.length != 0)
	{
		while(this.target.firstChild)
		{
			this.target.removeChild(this.target.firstChild);
		}

		var response = JSON.parse(responseText);
		for(var i = 0; i < response.length; i++)
		{
			var link = document.createElement("a");
			link.href = "/photos/index/" + response[i].user_id + "?topPhoto=" + response[i].photo_id;
			link.className += " resultLink";
			var img = document.createElement("img");
			img.src = "/images/" + response[i].file_name;
			img.className += " resultThumb";
			link.appendChild(img);
			this.target.appendChild(link);
		}
		//console.log(response);
	}*/
	console.log(responseText)
}
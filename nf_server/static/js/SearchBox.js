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
			// If user deletes everything in searchbox, make sure old
			// results get cleared.
			if(obj.searchField.value.length == 0)
			{
				while(obj.target.firstChild)
				{
					obj.target.removeChild(obj.target.firstChild);
				}
				obj.target.style.display = "none"
				return;
			}
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
	
	if(responseText.length != 0)
	{
		while(this.target.firstChild)
		{
			this.target.removeChild(this.target.firstChild);
		}

		var response = JSON.parse(responseText);
		this.articleHelper(response);
		//console.log(response);
	}
	//console.log(responseText)
}

SearchBox.prototype.articleHelper = function(response)
{
	var responseCount = 0;
	for(var id in response)
	{
		var span = document.createElement("span");
		span.classList.add("entry");
		
		var link = document.createElement("a");
		link.href = "/article/" + id;
		link.innerHTML = response[id];

		var addButton = document.createElement("button");
		addButton.classList.add("add_button");
		addButton.innerHTML = "+";

		span.appendChild(link);
		span.appendChild(addButton);		
		this.target.appendChild(span);
		
		console.log(response[id]);
		responseCount++;
	}	
	//this.target.style.width="250px";
	this.target.style.height= responseCount * 44 + 10 + "px";
	this.target.style.display = "block";
}
// For the main search page. Extends GenericSearchBox. Initial parameters
// are unchanged; see successHelper comment for details on how things get
// displayed.

function AllSearchBox(sbId, targetId, models)
{
	GenericSearchBox.call(this, sbId, targetId, models);
}

AllSearchBox.prototype = new GenericSearchBox();

// If the tags box is ticked, fire a tag search, otherwise cut straight
// to displaying them.
AllSearchBox.prototype.successHelper = function(response)
{
	this.responseData = response;

	if(this.tagCheckbox.checked)
	{
		var encQuery = encodeURIComponent(this.searchField.value);
		encQuery += "?models=" + encodeURIComponent(this.models);
		console.log("Encoded query:" + encQuery);
		Ajaxy.request("/fire_tag_search/" + encQuery, "GET", undefined,"", this.tagSearchHandler, null, this);
	}
	else
	{
		this.displayResults();
	}

}

// Merge the results from the initial search with those from the tag
// search.
AllSearchBox.prototype.tagSearchHandler = function(response)
{
	response = JSON.parse(response);
	for(var model in response)
	{
		for(var id in response[model])
		{
			this.responseData[model][id] = response[model][id];
		}
	}
	this.displayResults();
}

// Display results for different model types under a header for the model
// type. Each result is just a link to the appropriate page.
AllSearchBox.prototype.displayResults = function()
{
	var response = this.responseData;
	for(var model in response)
	{

		if(Object.keys(response[model]).length > 0)
		{
			//console.log(model);
			var header = document.createElement("h1");
			header.textContent = model.charAt(0).toUpperCase() + model.slice(1);
			this.target.appendChild(header);
		}

		for(var id in response[model])
		{
			//console.log(id + " " + response[model][id]);
			var span = document.createElement("span");
			span.classList.add("entry");
			var link = document.createElement("a");

			switch(model)
			{
				case 'articles':
					link.href = "/article/" + id;
					break;
				case 'feeds':
					link.href = "/feed/" + id;
					break;
				case 'sources':
					link.href = "/source/" + id;
					break;
				case 'events':
					link.href = "/event/" + id;
					break;
				default:
					continue;
			}
			link.textContent = response[model][id];
			span.appendChild(link);
			this.target.appendChild(span);
		}

	}
	this.target.style.display = "block";
}

// Handles the filtering for our main seach page. If a checkbox is ticked,
// we should search through that model for matches. When the ticked-ness
// of a box changes, we should update results immediately.
AllSearchBox.prototype.addCheckbox = function(id)
{
	if(!this.checkboxes)
	{
		this.checkboxes = {};
	}
	
	var checkbox = document.getElementById(id);
	
	if(!checkbox)
	{
		return null;
	}else
	{
		this.checkboxes[id] = checkbox;
	}

	var that = this;
	this.checkboxes[id].onchange = function(event)
	{
		var newModels = "";
		for(var id in that.checkboxes)
		{
			if(that.checkboxes[id].checked)
			{
				var index = id.indexOf("_checkbox");
				var modelType = id.substring(0,index);
				
				if(newModels.length == 0)
				{
					newModels = modelType;
				}
				else
				{
					newModels += " " + modelType;
				}
			}
		}
		that.models = newModels;

		// So we update results tattaima.
		that.keyupHandler();
	}
}

// Similar to the above method, but we only need to check whether
// the box is checked when we fire a search, so just add a mini handler
// to re-fire searches when the box is (un)checked.
AllSearchBox.prototype.addTagCheckbox = function(id)
{
	var tagCheckbox = document.getElementById(id);
	if(!tagCheckbox)
	{
		return null;
	}
	else
	{
		this.tagCheckbox = tagCheckbox;
	}

	var that = this;
	this.tagCheckbox.onchange = function(event)
	{
		that.keyupHandler();
	}

}
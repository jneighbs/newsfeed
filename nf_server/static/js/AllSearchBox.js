function AllSearchBox(sbId, targetId, models)
{
	GenericSearchBox.call(this, sbId, targetId, models);
}

AllSearchBox.prototype = new GenericSearchBox();

// For the main search page.
// Display results for different model types under a header for the model
// type. Each result is just a link to the appropriate page.
AllSearchBox.prototype.successHelper = function(response)
{
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
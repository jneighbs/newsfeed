function CompactSearchBox(sbId, targetId, saveListId, models)
{
	GenericSearchBox.call(this, sbId, targetId, models);
	
	this.saveList = document.getElementById(saveListId);
	if(!this.saveList)
	{
		return;
	}
	
	this.resultCount = 0;
}

CompactSearchBox.prototype = new GenericSearchBox();

CompactSearchBox.prototype.successHelper = function(response)
{
	response = response[this.models];
	this.resultCount = 0;
	
	var idsToSkip = this.getIdsToSkip();
	
	for(var id in response)
	{
		if(id in idsToSkip)
		{
			continue;
		}

		var resultElement = this.createResultElement(id, response);			
		this.target.appendChild(resultElement);
		
		this.resultCount++;
	}

	this.resizeResultBox();

	this.houseKeeping();
}

// Loop over the saveList and return an object with all the
// IDs from that list as its properties.
CompactSearchBox.prototype.getIdsToSkip = function()
{
	var list = this.saveList.children
	var ids = {};
	for(var i = 0; i < list.length; i++)
	{
		var id = parseInt(list[i].firstElementChild.firstElementChild.value);
		ids[id] = "lala";
	}
	return ids;
}

// Make the result / target box large enough to hold all of the results.
CompactSearchBox.prototype.resizeResultBox = function()
{
	if(this.resultCount > 0)
	{
		this.target.style.height= this.resultCount * 44 + 10 + "px";
		this.target.style.display = "block";	
	}
	else
	{
		this.target.style.display = "none";
	}
}

CompactSearchBox.prototype.addEntryToSaveList = function(id, title)
{
	var li = document.createElement("li");
	var label = document.createElement("label");
	label.setAttribute("for", "id_" + this.models + "_" + this.saveList.children.length);
	var input = document.createElement("input");
	input.setAttribute("checked", "checked");
	input.id = "id_" + this.models + "_" + this.saveList.children.length;
	input.name = "articles";
	input.type = "checkbox";
	input.value = id;
	label.appendChild(input);
	label.innerHTML += title;
	li.appendChild(label);
	this.saveList.appendChild(li);
}

CompactSearchBox.prototype.houseKeeping = function() {}
CompactSearchBox.prototype.createResultElement = function() {}
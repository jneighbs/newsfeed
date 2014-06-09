// General-use, single-model search widget. Displays results in a 
// little, collapsible list underneath the search box and provides hooks
// for moving those results to a list of saved entries once they've
// been clicked on or what have you.
//
// Not a fully functional class; it is up to you to implement
// createResultElement which essentially controls how results are displayed.
// And clickhandlers for moving those results from the results list to the
// saveList is also your responsibility.
//
// Also provides houseKeeping as a hook for any cleanup that needs to happen
// after all result elements have been created and displayed, like displaying
// extra buttons or what have you.

function CompactSearchBox(sbId, targetId, saveListId, models)
{
	GenericSearchBox.call(this, sbId, targetId, models);
	
	this.saveList = document.getElementById(saveListId);
	if(!this.saveList)
	{
		return;
	}
	
	this.resultCount = 0;
	this.sbType = "";
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

		var resultElement = this.createResultElement(id, response[id]);
		if(resultElement)
		{
			this.target.appendChild(resultElement);
			this.resultCount++;
		}
	}


	this.resizeResultBox();

	this.houseKeeping();
}

// Loop over the saveList and return an object with all the
// IDs from that list as its properties.
CompactSearchBox.prototype.getIdsToSkip = function()
{
	var ids = {};
	if(!this.saveList)
	{
		return ids;
	}
	var list = this.saveList.children
	
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
	input.name = this.sbType;
	input.type = "checkbox";
	input.value = id;
	label.appendChild(input);
	label.innerHTML += title;
	li.appendChild(label);
	this.saveList.appendChild(li);
}

CompactSearchBox.prototype.houseKeeping = function() {}
CompactSearchBox.prototype.createResultElement = function() {}
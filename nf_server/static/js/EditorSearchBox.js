function EditorSearchBox(sbId, targetId, saveListId, models)
{
	CompactSearchBox.call(this, sbId, targetId, saveListId, models);
}

EditorSearchBox.prototype = new CompactSearchBox();

EditorSearchBox.prototype.createResultElement = function(id, response)
{
	var span = document.createElement("span");
	span.classList.add("entry");

	var addButton = document.createElement("button");
	addButton.classList.add("add_button");
	addButton.innerHTML = "+";

	var that = this;
	addButton.onclick = function(event)
	{
		event.preventDefault();
		that.addButtonClickHandler(id, response[id]);
	}

	span.innerText = response[id];
	span.appendChild(addButton);

	return span;
}

// Basically the same as the ArticleSB's addButton handler
EditorSearchBox.prototype.addButtonClickHandler = function(id, title)
{
	this.addEntryToSaveList(id, title);

	var searchResults = this.target.children;
	for(var i = 0; i < searchResults.length; i++)
	{
		if(searchResults[i].firstChild.nodeValue == title)
		{
			this.target.removeChild(searchResults[i]);
			break;
		}
	}
	this.keyupHandler();
}
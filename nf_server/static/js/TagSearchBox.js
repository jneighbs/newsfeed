function TagSearchBox(sbId, targetId, saveListId, models)
{
	CompactSearchBox.call(this, sbId, targetId, saveListId, models);
	this.sbType = "tags";
}

TagSearchBox.prototype = new CompactSearchBox();

TagSearchBox.prototype.createResultElement = function(id, response)
{
	var span = document.createElement("div");
	span.classList.add("entry");
	span.innerHTML = response;

	var that = this;
	span.onclick = function(event)
	{
		event.preventDefault();
		that.tagClickHandler(id, response);
	}

	return span;
}

TagSearchBox.prototype.tagClickHandler = function(id, title)
{

	if(id == -1)
	{
		this.addEntryToSaveList(title, title);
	}
	else
	{
		this.addEntryToSaveList(id, title);
	}

	var searchResults = this.target.children;
	for(var i = 0; i < searchResults.length; i++)
	{
		if(searchResults[i].innerText == title)
		{
			this.target.removeChild(searchResults[i]);
		}
	}

	if(searchResults.length > 0)
	{
		//this.target.style.height= searchResults.length * 44 + 10 + "px";
		this.target.style.display = "block";	
	}
	else
	{
		this.target.style.display = "none";
	}

	//this.searchBox.removeChild(this.createTagButton);
	//this.createTagButton = null;
}

TagSearchBox.prototype.houseKeeping = function()
{
	if(!this.createTagButton)
	{
		this.createTagButton = document.createElement("input");
		this.createTagButton.type = "button";
		this.createTagButton.value = "Create";
		this.createTagButton.classList.add("btn");
		this.createTagButton.classList.add("btn-group");
		this.createTagButton.classList.add("create-button-tag");

		var that = this;
		this.createTagButton.onclick = function(event)
		{

			that.tagClickHandler(-1, that.searchField.value);
			that.searchField.value = "";
			that.keyupHandler();
			//that.searchBox.removeChild(that.createTagButton);
			//that.createTagButton = null;
		}

		this.searchBox.appendChild(this.createTagButton);
	}

	var queryInSaveList = false;
	var titles = this.getSaveListTitles();
	for(var i = 0; i < titles.length; i++)
	{
		if(this.searchField.value == titles[i])
		{
			queryInSaveList = true;
		}
	}
	if(queryInSaveList)
	{
		this.createTagButton.setAttribute("disabled", "disabled");
	}
	else
	{
		this.createTagButton.removeAttribute("disabled");
	}
}

TagSearchBox.prototype.getSaveListTitles = function()
{
	var titles = [];
	for(var i = 0; i < this.saveList.children.length; i++)
	{
		titles.push(this.saveList.children[i].firstElementChild.innerText);
	}
	return titles;
}

TagSearchBox.prototype.searchBoxEmptied = function()
{
	this.searchBox.removeChild(this.createTagButton);
	this.createTagButton = null;
}
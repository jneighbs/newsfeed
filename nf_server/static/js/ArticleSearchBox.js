function ArticleSearchBox(sbId, targetId, saveListId, models)
{
	CompactSearchBox.call(this, sbId, targetId, saveListId, models);
	this.sbType = "articles";
}

ArticleSearchBox.prototype = new CompactSearchBox();

ArticleSearchBox.prototype.createResultElement = function(id, response)
{
	var span = document.createElement("div");
	span.classList.add("entry");
	
	var link = document.createElement("a");
	link.href = "/article/" + id;
	link.innerHTML = response.title;
	link.setAttribute("target", "blank");

	var addButton = document.createElement("button");
	addButton.classList.add("add_button");
	addButton.classList.add("btn");
	addButton.classList.add("btn-default");
	addButton.innerHTML = "+";

	var that = this;
	//avoid the JS for-loop trap
	(function(id, title, addButton)
	{
		addButton.onclick = function(event)
		{
			event.preventDefault();
			that.addButtonClickHandler(id, title);
		}
	})(id, response.title, addButton);

	span.appendChild(link);
	span.appendChild(addButton);

	return span;
}

// On clicking the '+' button on a search result, add it to the articles list,
// and remove it from the search results.
ArticleSearchBox.prototype.addButtonClickHandler = function(id, title)
{
	this.addEntryToSaveList(id, title);

	var searchResults = this.target.children;
	for(var i = 0; i < searchResults.length; i++)
	{
		if(searchResults[i].firstElementChild.innerText == title)
		{
			var href = searchResults[i].firstElementChild.href;
			var suffix = "article/" + id;
			if(href.indexOf(suffix, href.length - suffix.length) !== -1)
			{
				this.target.removeChild(searchResults[i]);
				break;
			}
		}
	}
	this.keyupHandler();
}
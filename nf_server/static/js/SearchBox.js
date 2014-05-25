function SearchBox(sbId, targetId, models)
{
	this.successHandler = this.articleHelper;
	this.target = document.getElementById(targetId);
	this.models = models;
	this.articlesList = null;

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
		var that = this;
		this.searchField.onkeyup = function(event)
		{
			that.keyupHandler();
		}
	}
	else
	{
		return null;
	}
}

// Fire a search on keyup unless there's nothing in the searchbox.
SearchBox.prototype.keyupHandler = function()
{
	// If user deletes everything in searchbox, make sure old
	// results get cleared.
	if(this.searchField.value.length == 0)
	{
		while(this.target.firstChild)
		{
			this.target.removeChild(this.target.firstChild);
		}
		this.target.style.display = "none"
		return;
	}
	var encQuery = encodeURIComponent(this.searchField.value);
	encQuery += "?models=" + encodeURIComponent(this.models);
	console.log("Encoded query:" + encQuery);
	Ajaxy.request("/fire_search/" + encQuery, "GET", undefined,"", this.ajaxSuccessHandler, null, this);
}


// Handles the filtering for our main seach page. If a checkbox is ticked,
// we should search through that model for matches. When the ticked-ness
// of a box changes, we should update results immediately.
SearchBox.prototype.addCheckbox = function(id)
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

// Switch witch handler we use when the AJAX call succeeds. The articleHelper
// displays resulst in a neat little box of limited size with buttons (non-functional for now)
// for adding articles to an event. The allHelper just displays errythang.
SearchBox.prototype.articleMode = function()
{
	this.successHandler = this.articleHelper;
}

SearchBox.prototype.allMode = function()
{
	this.successHandler = this.allHelper;
}

// The first step for when we succeed making our AJAX request. Tear 
// everything out of the target div so that it's ready to go, then
// parse the JSON response and pass it forward to whatever handler's
// been set for the page.
SearchBox.prototype.ajaxSuccessHandler = function(responseText)
{
	
	if(responseText.length != 0)
	{
		while(this.target.firstChild)
		{
			this.target.removeChild(this.target.firstChild);
		}

		var response = JSON.parse(responseText);
		this.successHandler(response);
	}
}

// For the main search page.
// Display results for different model types under a header for the model
// type. Each result is just a link to the appropriate page.
SearchBox.prototype.allHelper = function(response)
{
	for(var model in response)
	{

		if(Object.keys(response[model]).length > 0)
		{
			console.log(model);
			var header = document.createElement("h1");
			header.textContent = model.charAt(0).toUpperCase() + model.slice(1);
			this.target.appendChild(header);
		}

		for(var id in response[model])
		{
			console.log(id + " " + response[model][id]);
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

// For the create_event page.
// Dumps results into a mini-div under the actual search bar. Div has fixed
// width & a max height, is scrollable if there are too many things to display,
// and each entry is a link to the article and a button for adding it to
// the event.
SearchBox.prototype.articleHelper = function(response)
{
	response = response['articles'];
	var responseCount = 0;
	var ids = getArticleListIds(document.getElementById(this.articlesList).children);
	for(var id in response)
	{
		// Don't display articles that are already part of the event.
		if(id in ids)
		{
			continue;
		}

		var span = document.createElement("span");
		span.classList.add("entry");
		
		var link = document.createElement("a");
		link.href = "/article/" + id;
		link.innerHTML = response[id];

		var addButton = document.createElement("button");
		addButton.classList.add("add_button");
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
		})(id, response[id], addButton);


		span.appendChild(link);
		span.appendChild(addButton);		
		this.target.appendChild(span);
		
		responseCount++;
	}	
	this.target.style.height= responseCount * 44 + 10 + "px";
	this.target.style.display = "block";

	// Loop over the articlesList and return an object with all the
	// article IDs from that list as its properties.
	function getArticleListIds(list)
	{
		var ids = {};
		for(var i = 0; i < list.length; i++)
		{
			var id = parseInt(list[i].firstElementChild.firstElementChild.value);
			ids[id] = "lala";
		}
		return ids;
	}
}

// On clicking the '+' button on a search result, add it to the articles list,
// and remove it from the search results.
SearchBox.prototype.addButtonClickHandler = function(id, title)
{
	var list = document.getElementById(this.articlesList);
	if(!list)
	{
		return;
	}
	console.log(this.articlesList + " " + id + " " + title);

	var li = document.createElement("li");
	var label = document.createElement("label");
	label.setAttribute("for", "id_articles_" + list.children.length);
	var input = document.createElement("input");
	input.setAttribute("checked", "checked");
	input.id = "id_articles_" + list.children.length;
	input.name = "articles";
	input.type = "checkbox";
	input.value = id;
	label.appendChild(input);
	label.innerHTML += title;
	li.appendChild(label);
	list.appendChild(li);

	var searchResults = this.target.children;
	for(var i = 0; i < searchResults.length; i++)
	{
		if(searchResults[i].firstElementChild.innerText = title)
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
}
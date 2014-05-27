// A generic search class. Takes the id of a div containing an input from
// which to read search terms, and the id of a div to put results into. Also
// takes a models parameter that is a space-separated string specifying all
// the database models to search over, e.g. "articles tags".
// Check utils.py for currently supported models; includes but is not
// limited to articles, events, sources, feeds, users, and tags.
//
// NB: This is meant to be extended and not used directly. successHelper
// needs to be filled in for any results to actually be displayed.
// Also provides searchBoxEmptied as a hook in case you need to do sometihing
// when that happens.
function GenericSearchBox(sbId, targetId, models)
{
	this.target = document.getElementById(targetId);
	this.models = models;
	this.articlesList = null;

	this.searchBox = document.getElementById(sbId);
	if(!this.searchBox)
	{
		return null;
	}
	var inputs = this.searchBox.getElementsByTagName("input");
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
GenericSearchBox.prototype.keyupHandler = function()
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

		this.searchBoxEmptied();
		return;
	}

	var encQuery = encodeURIComponent(this.searchField.value);
	encQuery += "?models=" + encodeURIComponent(this.models);
	console.log("Encoded query:" + encQuery);
	Ajaxy.request("/fire_search/" + encQuery, "GET", undefined,"", this.ajaxSuccessHandler, null, this);
}

// The first step for when we succeed making our AJAX request. Tear 
// everything out of the target div so that it's ready to go, then
// parse the JSON response and pass it forward to whatever handler's
// been set for the page.
GenericSearchBox.prototype.ajaxSuccessHandler = function(responseText)
{
	
	if(responseText.length != 0)
	{
		while(this.target.firstChild)
		{
			this.target.removeChild(this.target.firstChild);
		}

		var response = JSON.parse(responseText);
		this.successHelper(response);
	}
}

GenericSearchBox.prototype.successHelper = function(response) {}
GenericSearchBox.prototype.searchBoxEmptied = function() {}
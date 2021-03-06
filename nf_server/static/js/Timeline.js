// A class that creates / encapsulates a chronological series
// of text entries. Entries can be added and edited. Just
// requires a div to stick everything in and handles all
// DOM object creation and rearranging. Can be initialized
// with an array of timeline entries where each array element
// is in turn an array of containing an already-formatted date string
// and text.

function Timeline(container_id, timelineEntries)
{
	this.containerElem = document.getElementById(container_id);
	if(!this.containerElem)
	{
		return null;
	}

	this.entryElems = []

	for(var i = 0; i < timelineEntries.length; i++)
	{
		entry = timelineEntries[i];
		var entryElement = this.createEntryElement(entry[0], entry[1], entry[2]);
		this.containerElem.appendChild(entryElement);
		this.entryElems.push(entryElement);
	}

	this.newEntryElem = this.createNewEntryElement();
	this.containerElem.appendChild(this.newEntryElem);
}

Timeline.prototype.createEntryElement = function(date, text, pk)
{
	var outerDiv = document.createElement("div");
	outerDiv.classList.add("timeline_entry");
	outerDiv.classList.add("col-md-4");
	
	var dateDiv = document.createElement("div");
	dateDiv.classList.add("date");
	dateDiv.innerText = date;
	
	var editButton = document.createElement("button");
	editButton.classList.add("btn")
	editButton.classList.add("btn-default");
	editButton.classList.add("create-button-timeline");
	editButton.innerText = "Edit";

	var that = this;
	editButton.onclick = function(event)
	{
		event.preventDefault();
		that.editButtonClickHandler(outerDiv);
	}

	var textarea = document.createElement("textarea");
	textarea.setAttribute("form", "event_form");
	textarea.setAttribute("readonly", "readonly");
	textarea.setAttribute("name", "timelineEntry_" + pk);
	textarea.className += "form-control";
	textarea.innerText = text;

	outerDiv.appendChild(dateDiv);
	outerDiv.appendChild(textarea);
	outerDiv.appendChild(editButton);

/*	var outerOuterDiv = document.createElement("div");
	outerOuterDiv.classList.add("form-group");
	outerOuterDiv.appendChild(outerDiv);*/

	return outerDiv;
}

Timeline.prototype.createNewEntryElement = function()
{
	var outerDiv = document.createElement("div");
	outerDiv.classList.add("timeline_entry");
	outerDiv.classList.add("new_timeline_entry");
	outerDiv.classList.add("col-md-4");

	outerDiv.appendChild(document.createElement("textarea"));

	var button = document.createElement("button");
	button.classList.add("btn")
	button.classList.add("btn-default");
	button.classList.add("create-button-timeline");
	button.innerText = "Add";

	var that = this;
	button.onclick = function(event)
	{
		event.preventDefault();
		that.addButtonClickHandler();
	}

	outerDiv.appendChild(button);

/*	var outerOuterDiv = document.createElement("div");
	outerOuterDiv.classList.add("form-group");
	outerOuterDiv.appendChild(outerDiv);*/

	return outerDiv;
}

Timeline.prototype.addButtonClickHandler = function()
{
	var text = null;
	for(var i = 0; i < this.newEntryElem.children.length; i++)
	{
		var nextChild = this.newEntryElem.children[i];
		if(nextChild.tagName.toLowerCase() == "textarea")
		{
			text = nextChild.value;
			nextChild.value = "";
		}
	}

	if(text)
	{
		var entry = this.createEntryElement(PrettyDate(), text, "add");
		this.containerElem.insertBefore(entry, this.newEntryElem);
		this.entryElems.push(entry);
	}
}

Timeline.prototype.editButtonClickHandler = function(entry)
{
	for(var i = 0; i < entry.children.length; i++)
	{
		var nextChild = entry.children[i];
		if(nextChild.tagName.toLowerCase() == "textarea")
		{
			nextChild.removeAttribute("readonly");
		}

		if(nextChild.tagName.toLowerCase() == "button")
		{
			nextChild.innerText = "Save";
			var that = this;
			nextChild.onclick = function(event)
			{
				event.preventDefault();
				that.saveButtonClickHandler(entry);
			}
		}
	}
}

Timeline.prototype.saveButtonClickHandler = function(entry)
{
	for(var i = 0; i < entry.children.length; i++)
	{
		var nextChild = entry.children[i];
		if(nextChild.tagName.toLowerCase() == "textarea")
		{
			nextChild.setAttribute("readonly", "readonly");
		}

		if(nextChild.tagName.toLowerCase() == "button")
		{
			nextChild.innerText = "Edit";
			var that = this;
			nextChild.onclick = function(event)
			{
				event.preventDefault();
				that.editButtonClickHandler(entry);
			}
		}
	}
}
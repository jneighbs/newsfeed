function NewSourceValidator(name_id, description_id, url_id, csrf)
{
	this.nameField = document.getElementById(name_id);
	if(!this.nameField || this.nameField.nodeName.toLowerCase() != 'input' || this.nameField.type != 'text')
	{
		return null;
	}

	this.descriptionField = document.getElementById(description_id);
	if(!this.descriptionField || this.descriptionField.nodeName.toLowerCase() != 'textarea')
	{
		return null;
	}

	this.urlField = document.getElementById(url_id);
	if(!this.urlField || this.urlField.nodeName.toLowerCase() != 'input' || this.urlField.type != 'text')
	{
		return null;
	}

	this.csrf = csrf;
	if(!csrf)
	{
		return null;
	}

	var that = this;

	this.nameField.onkeyup = function(event)
	{
		that.keyupHandler();
	}

	this.descriptionField.onkeyup = function(event)
	{
		that.keyupHandler();
	}

	this.urlField.onkeyup = function(event)
	{
		that.keyupHandler();
	}
}

NewSourceValidator.prototype.keyupHandler = function()
{
	data = {
		"name": this.nameField.value,
		"description": this.descriptionField.value,
		"url": this.urlField.value,
	};
	Ajaxy.request("/new_source/", "POST", JSON.stringify(data), "", this.validateCallback, null, this, this.csrf);
}

NewSourceValidator.prototype.validateCallback = function(response)
{
	var allGood = true;
	response = JSON.parse(response);
	for(var fieldName in response)
	{
		var errorMessage = document.getElementById("id_" + fieldName + "_error");
		if(errorMessage)
		{
			if(response[fieldName] == true)
			{

				errorMessage.style.display = "none";
			}
			else
			{
				errorMessage.style.display = "block";
				allGood = false;
			}
		}
	}

	var submitButton = document.getElementById("submit_button");
	if(submitButton)
	{
		if(allGood)
		{
			submitButton.removeAttribute("disabled");
		}
		else
		{
			submitButton.setAttribute("disabled", "disabled");
		}
	}

}
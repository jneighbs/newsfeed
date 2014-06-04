function FieldValidator(IDs, url, csrf)
{
	if(!IDs || !url || !csrf)
	{
		return null;
	}

	this.fields = [];
	for(var i = 0; i < IDs.length; i++)
	{
		var fieldObj = {
			"name": IDs[i],
			"elem": document.getElementById("id_" + IDs[i]),
		}
		if(fieldObj && ((fieldObj.elem.nodeName.toLowerCase() == 'input' && fieldObj.elem.type == 'text') || (fieldObj.elem.nodeName.toLowerCase() == 'textarea')))
		{
			this.fields.push(fieldObj);
			var that = this;
			fieldObj.elem.onkeyup = function(event)
			{
				that.keyupHandler();
			}
		}
	}

	this.url = url;
	this.csrf = csrf;

	this.keyupHandler();
}

FieldValidator.prototype.keyupHandler = function()
{
	data = {};
	for(var i = 0; i < this.fields.length; i++)
	{
		data[this.fields[i].name] = this.fields[i].elem.value;
	}
	Ajaxy.request(this.url, "POST", JSON.stringify(data), "", this.successCallback, this.errorCallback, this, this.csrf);
}

FieldValidator.prototype.successCallback = function(response)
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
				errorMessage.innerText = response[fieldName];
				allGood = false;
			}
		}
	}

	var submitButton = document.getElementById("save_button");
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

FieldValidator.prototype.errorCallback = function()
{
	console.log("Field validator failed...");
	console.log(this.fields);
	console.log(this.url);
}
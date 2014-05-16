function SearchHelper(id)
{
	this.checkbox = document.getElementById(id);
	if(!this.checkbox)
	{
		return null;
	}

	var that = this;
	this.checkbox.onchange = function(event)
	{
		console.log(that.checkbox.checked)
	}
}
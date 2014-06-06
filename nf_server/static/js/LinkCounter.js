function LinkCounter()
{
	var allLinks = document.getElementsByTagName("a");
	var that = this;
	for(var i = 0; i < allLinks.length; i++)
	{
		allLinks[i].onclick = function(event)
		{
			that.clickHandler();
		}
	}
}

LinkCounter.prototype.clickHandler = function()
{
	console.log("asdf");
}
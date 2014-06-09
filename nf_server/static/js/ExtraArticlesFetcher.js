function ExtraArticlesFetcher(model, modelId)
{
	if(!model || !modelId)
	{
		return null;
	}
	this.model = model;
	this.modelId = modelId;

	this.articlesList = document.getElementById("articles_list");
	if(!this.articlesList)
	{
		return null;
	}

	this.loadButton = document.getElementById("load_button");
	if(!this.loadButton)
	{
		return null;
	}

	var that = this;
	this.loadButton.onclick = function(event)
	{
		that.loadMore();
	}

	this.chunksLoaded = 1;
}

ExtraArticlesFetcher.prototype.loadMore = function()
{
	data = {
		"model": this.model,
		"id": this.modelId,
		"chunksLoaded": this.chunksLoaded,
	}
	this.chunksLoaded += 1;
	$.get("/load_more/", data, this.onLoadSuccess)
}

ExtraArticlesFetcher.prototype.onLoadSuccess = function(response)
{
	console.log("load succeeded...");
	console.log(response);
	//var articles = JSON.parse(response);
	for(var i = 0; i < response.length; i++)
	{
		var article = response[i];
		var li = document.createElement("li");
		
		var link = document.createElement("a");
		link.setAttribute("target", "blank");
		link.href = "/article/" + article.id;
		link.innerText = article.title;
		li.appendChild(link);
		
		var div = document.createElement("div");
		div.classList.add("date");
		div.innerText = article.pubDate + "|" + article.sourceTitle;
		li.appendChild(div);

		li.appendChild(document.createTextNode(article.summaryText));
		li.appendChild(document.createElement("br"));
		li.appendChild(document.createElement("br"));

		document.getElementById("articles_list").appendChild(li);
	}
}
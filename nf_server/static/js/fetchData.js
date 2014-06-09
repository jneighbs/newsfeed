searchTerm = ""

 var fetchData = function(){
	// TODO grab search term
	searchTerm = "#lol"
	fetchTweets()
}

var fetchTweets = function(){

	url = "/load_tweets/"
	data = {
		"searchTerm": searchTerm,
	}
	$.get(url, data, success)
}

var success = function(response){

	response = JSON.parse(response);

	date_html = '<div class="date">' + response.pub_date + '|' + response.searchTerm + '</div>';
	console.log(date_html)

	$("#right-bar-block-tweets").prepend(date_html)
	$("#right-bar-block-tweets").prepend("<p>" + response.text + "</p>")
	setTimeout(fetchTweets, 15000)

}


$(document).ready(fetchData)
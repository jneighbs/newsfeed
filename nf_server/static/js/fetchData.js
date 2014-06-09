searchTerm = ""
var i = 0

 var fetchData = function(){
	// TODO grab search term

	searchTerm = "#tracymorgan";
	domObj = $("#tweet-searchTerm");
	if(domObj.length != 0){
		searchTerm = "#" + domObj[0].innerHTML.replace(/ /g, "");
	}

	// fetchTweets();
}

var fetchTweets = function(){

	url = "/load_tweets/"
	data = {
		"searchTerm": searchTerm,
	}
	$.get(url, data, success)
}

var success = function(response){

	i++
	response = JSON.parse(response);

	date_html = '<div class="date">' + response.pub_date + '|' + response.searchTerm + '</div>';
	console.log(date_html)

	$("#right-bar-block-tweets").prepend(date_html)
	$("#right-bar-block-tweets").prepend("<p>" + response.text + "</p>")
	// if(i<=1){
	// 	setTimeout(fetchTweets, 10000)
	// }

}


$(document).ready(fetchData)
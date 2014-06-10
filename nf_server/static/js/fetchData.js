searchTerm = ""
var i = 0

 var fetchData = function(){

	searchTerm = "#tracymorgan";
	domObj = $("#tweet-searchTerm");
	if(domObj.length != 0){
		searchTerm = "#" + domObj[0].innerHTML.replace(/ /g, "");
	}

	fetchTweets();
}

var fetchTweets = function(){

	url = "/load_tweets/"
	data = {
		"searchTerm": searchTerm,
	}
	$.get(url, data, success)
}

var success = function(response){

	i++;
	response = JSON.parse(response);
	tweet_html='<li><a href="https://twitter.com/'+response.screenname+'/status/'+response.tweet_id+' target="_blank" class="tweet">'+response.text+'</a></li>';
/*	tweet_html = '<p class="tweet_hello">' + response.text + '</p>';
*/
	$("#right-bar-block-tweets").prepend(tweet_html)
	// if(i<=1){
	// 	setTimeout(fetchTweets, 10000)
	// }
}


$(document).ready(fetchData)
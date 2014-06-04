function Ajaxy() {}

/*
Executes an asynchronous XMLHttpRequest using the provided method and URL. Can fill
the element corresponding to a provided element ID with the response text. Takes optional
success and error callback functions.

Return: 0 on success, -1 if the method is invalid, -2 if the URL is not a string

URL: the URL for the ajax request

method: the method for the ajax request. Valid methods are GET and POST

Optional Arguments:

elementId: the ID of an HTML element whose inner HTML will be filled with the response text

successCallback: invoked if the request returns with status 200.

errorCallback: populated with the XMLHttpRequest object, the error status text,
and the error code.

context: the context within which to invoke the success or error callback

*/

Ajaxy.request = function(URL, method, data, elementId, successCallback, errorCallback, context, csrf) {
	// Check that method is valid
	method = method.toUpperCase();
	if(!methodIsValid(method))
	{
		return -1;
	}

	// Check that URL is (vaguely) valid
	if(!urlIsValid(URL))
	{
		return -2;
	}

	var xhr = new XMLHttpRequest();
	xhr.open(method, URL);
	if(method == "POST" && typeof data !== 'undefined')
	{
		xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		//xhr.setRequestHeader("Content-length", data.length);
		//xhr.setRequestHeader("Connection", "close");
		xhr.setRequestHeader("X-CSRFToken", csrf)
	}

	

	xhr.onreadystatechange = function() {

		// Do nothing until the request is complete.
		if (this.readyState != 4) {
            return;
        }
        // If status is OK ...
        if (this.status == 200)
        {
            console.log("Response is " + this.responseText);

            // If elementId is supplied and corresponds to an element in the DOM,
            // fill its inner HTML with the response text.
            if(typeof elementId !== 'undefined')
            {
            	var element = document.getElementById(elementId);
            	if(element != null)
            	{
            		element.innerHTML = this.responseText;
            	}
            }

			// finally, execute our callback
			if(typeof successCallback !== 'undefined')
			{
				// Use the context for the callback if it's defined.
				if(typeof context !== 'undefined')
				{
					successCallback.call(context, this.responseText);
				}
				else
				{
					successCallback(this.responseText);
				}
				
			}

            return;
        // If not OK, invoke errorCallback if defined.
        } else if(typeof errorCallback !== 'undefined')
        {
        	// Use the context for the callback if it's defined.
        	if(typeof context !== 'undefined')
			{
				errorCallback.call(context, this.responseText);
			}
			else
			{
				errorCallback(this.responseText);
			}
        }
		
	};

	if(method == "POST" && typeof data == 'string')
	{
		xhr.send(data);
	}
	else
	{
		xhr.send();
	}
	return 0;

	// Checks that the method is a valid HTTP(S) method
	function methodIsValid(method)
	{
		var methods = ["GET", "POST"];
		
		for(var i=0; i < methods.length; i++)
		{
			if(methods[i] == method)
			{
				return true;
			}
		}
		return false;
	}

	// Fill these in ...
	function urlIsValid(URL)
	{
		if(typeof URL != 'string')
		{
			return false;
		}

		if(URL.length == 0)
		{
			return false;
		}

		return true;
	}
}

$("#movies_datalist").autocomplete({
	source: function(request, response){
		var results = $.ui.autocomplete.filter(movie_list, request.term);
		response(results.slice(0, 10));
	}
});
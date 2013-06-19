function getURLParameter(name) {
	return decodeURI(
		(RegExp(name + '=' + '(.+?)(&|$)').exec(location.search)||[,null])[1]
	);
}

$(document).ready(function(){
	var selected = getURLParameter("sortselect");
	if(selected !== "null"){
		$('#sortselect').val(selected);
	}else {
		$('#sortselect').val("plays");
	}
	
});

$(function() {
	$("#searchtype button").click(function () {
		$("#sortvalue").val($(this).attr("id"));
	});
	
	$('#sortselect').change(function () {
		$("#sortvalue").val($(this).val());
	});
});
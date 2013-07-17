function init(){
    $('form').ajaxForm(function(response){
        card_detail(response);
    });
}
function close_overlay(){
	$('#overlay').hide();
    location.reload();
}

function show_overlay(){
	$('#overlay').show();
}

function card_detail(key){
    $('#card_content').load('/card_detail?key='+key,function(){
        init();
    });
    show_overlay();
}

$('document').ready(function(){
	$('.close-button').click(function(){
		close_overlay();
	});
    $('tr').click(function(){
        card_detail($(this).attr('key'));
    });
});

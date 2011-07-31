jQuery.fn.liveSearch = function(config){
    var config = jQuery.extend({
            typeDelay: 600
        }, config);

    var timer;

    $(this).live('keyup', function(){
       if (timer) {
           clearTimeout(timer);
       }
       var query = this.value;
       var that = this;
       timer = setTimeout(function(){
           var form = $(that).closest('form');
           app.router.redrawSearch = false;
           jQuery.bbq.pushState('#' + form.attr('action').split(location.host).pop() + '?' + form.serialize());
       }, config.typeDelay);
    });

    return this;
}

$(function(){
   $('#js-search-form input:text').liveSearch();
});
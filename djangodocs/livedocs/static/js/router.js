app.router = (function () {
    var router = {
        redrawSearch: true
    }

    var blockHashChangeEvent = false;
    var oldHash = null;

    function changeHashWithNoReload(jqXHR) {
        var changeHash = jqXHR.getResponseHeader('X-Ajax-Redirect');
        if (changeHash) {
            window.location.replace(location.protocol+'//'+location.host+'/#'+changeHash);
            blockHashChangeEvent = true;
        }
    }

    function changePageTitle(jqXHR) {
        var title = jqXHR.getResponseHeader('X-Ajax-PageTitle');
        if (title) {
            document.title = decodeURIComponent(title);
        }
    }
    
    router.hashChangeCallback = function (event) {
        if (blockHashChangeEvent) {
            blockHashChangeEvent = false;
            return;
        }

        var newHash = event.fragment;
        if (!(oldHash === null && newHash == '')) {
            $.ajax({
                url: newHash,
                dataType: 'html',
                success: function(html, text, jqXHR) {
                    changeHashWithNoReload(jqXHR);
                    changePageTitle(jqXHR);
                    if (router.redrawSearch) {
                        $('#js-content').html(html);
                        $('#js-search-form input:first').focus();
                    } else {
                        $('#js-main-content').html($(html).find('#js-main-content').html());
                        $('#js-version').html($(html).find('#js-version').html());
                    }
                    var parts = newHash.split('/');
                    var lastId = parts[parts.length-2];
                    console.log(lastId);
                    $.scrollTo($('#'+ lastId), {offset:{ top:-100}});
                    router.redrawSearch = true;
                }
            });
        }

        oldHash = newHash;
    };

    return router;

}());

$(function(){
    $(window).bind('hashchange', app.router.hashChangeCallback);
    $(window).trigger('hashchange');

    // Handle normal urls as Ajax hash urls
    $('.js-ajax').live('click', function(e){
        e.preventDefault();
        jQuery.bbq.pushState('#' + $(this).attr('href').split(location.host).pop());
    });

    // Search form ajax handling
    $('#js-search-form').live('submit', function(e){
        e.preventDefault();
        jQuery.bbq.pushState('#' + $(this).attr('action').split(location.host).pop() + '?' + $(this).serialize());
    });
});
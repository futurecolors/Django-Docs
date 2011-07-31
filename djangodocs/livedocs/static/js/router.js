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

    function scrollContent(newHash) {
        var parts = newHash.split('/');
        var lastId = parts[parts.length-2];
        if ($('#'+ lastId).length == 0 && $('.b-results__link').length) {
            var parts = $('.b-results__link').attr('href').split('/');
            var lastId = parts[parts.length-2];
        }
        if ($('#'+ lastId).length) {
            $.scrollTo($('#'+ lastId), {offset:{ top:-100}});
        } else {
            $.scrollTo(0);
        }
    }
    
    router.hashChangeCallback = function (event) {
        if (blockHashChangeEvent) {
            blockHashChangeEvent = false;
            return;
        }

        var newHash = event.fragment;
        if (!(oldHash === null && newHash == '')) {
            $('.js-ajax-loader').trigger('start');
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
                    scrollContent(newHash);
                    $('.js-ajax-loader').trigger('stop');
                    router.redrawSearch = true;
                },
                error: function(){
                    $('.js-ajax-loader').trigger('stop');
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

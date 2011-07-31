app.router = (function () {
    var router = {
        loadedSectionHtml: ''
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
                    $('#js-content').html(html);
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

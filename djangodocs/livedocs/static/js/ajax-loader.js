$(function(){
    var loaderAnimation = false;

    $('.js-ajax-loader')
        .bind('start', function(){
            loaderAnimation = true;
            animateLoader($(this).show());
        })
        .bind('stop', function(){
            loaderAnimation = false;
            $(this).hide();
        });

    function animateLoader($loader) {
        if (loaderAnimation) {
            var position = $loader.css('backgroundPositionX');
            $loader.css('backgroundPositionX', position + 30);
            setTimeout(function(){animateLoader($loader)}, 40);
        }
    }
});

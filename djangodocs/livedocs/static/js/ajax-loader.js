$(function(){
    var loaderAnimation = false;
    var position = 0;

    $('.js-ajax-loader')
        .live('start', function(){
            loaderAnimation = true;
            animateLoader($(this).show());
        })
        .live('stop', function(){
            loaderAnimation = false;
            $(this).hide();
        });

    function animateLoader($loader) {
        if (loaderAnimation) {
            position += 30;
            if (position > 2000) {
                position = 0;
            }
            $loader.css('backgroundPosition', '-' + position + 'px 0px');
            setTimeout(function(){animateLoader($loader)}, 40);
        }
    }
});

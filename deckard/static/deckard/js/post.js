$(function(){
    $('.dkr-plus, .dkr-minus').on('click', function(e){
         e.preventDefault();
         $.ajax({
             url: $(this).attr('data-link'),
             success: $.proxy(function(newRating){
             var parent = $(this).parents('.dkr-vertical-rating').eq(0);
                oldRating = parent.find('.dkr-rating').eq(0).text();
                if (newRating != oldRating) {
                    parent.find('.dkr-active').eq(0).removeClass('dkr-active');
                    $(this).toggleClass('dkr-active', (newRating != oldRating) && (newRating != 0));
                    parent.find('.dkr-rating').eq(0).text(newRating);
                }
             }, this)
         })
      });
});

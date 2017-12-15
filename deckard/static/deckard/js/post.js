$(function(){
    $('.dkr-plus, .dkr-minus').on('click', function(e){
         e.preventDefault();
         $.ajax({
             url: $(this).attr('data-link'),
             success: $.proxy(function(newRating){
                $(this).parents('.dkr-vertical-rating').eq(0).find('.dkr-rating').eq(0).text(newRating);
             }, this)
         })
      });
});

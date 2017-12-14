$(function(){
    $('.like').on('click', function(e){
         e.preventDefault();
         $.ajax({
             url: $(this).attr('data-link'),
             success: $.proxy(function(newLikeCount){
                var oldLikeCount =  $(this).parents('div').eq(0).children('.dkr-like-count').eq(0).text();
                $(this).toggleClass("red", newLikeCount > oldLikeCount);
                $(this).parents('div').eq(0).children('.dkr-like-count').eq(0).text(newLikeCount);
             }, this)
         })
      });
});

$(function(){
    $('.like').on('click', function(e){
         e.preventDefault();
         $.ajax({
             url: $(this).attr('data-link'),
             success: $.proxy(function(){
                $(this).toggleClass("red");
                var old_like_count = $(this).parents('div').eq(0).children('.dkr-like-count').eq(0).text();
                var like_diff = -1;
                if ($(this).hasClass("red")) {  // + 1 like
                    like_diff = 1;
                }
                $(this).parents('div').eq(0).children('.dkr-like-count').eq(0).text(Number(old_like_count) + like_diff);
                console.log(like_diff + ' like');
             }, this)
         })
      });
});

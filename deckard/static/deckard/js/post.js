$(function(){
    $('.like').on('click', function(e){
         e.preventDefault();
         $.ajax({
             url: $(this).attr('data-link'),
             success: $.proxy(function(){
                $(this).toggleClass("red");
                console.log('Liked/disliked!');
             }, this)
         })
      });
});

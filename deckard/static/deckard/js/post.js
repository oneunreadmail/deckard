$(function(){
    // Post rating AJAX functionality - plus/minus
    $('.dkr-plus, .dkr-minus').on('click', function(e){
         e.preventDefault();
         $.ajax({
             url: $(this).data('link'),
             success: $.proxy(function(newRating){
             var parent = $(this).parents('.dkr-vertical-rating').eq(0);
                oldRating = parent.find('.dkr-rating').eq(0).text();
                if (newRating != oldRating) {
                    parent.find('.dkr-active').eq(0).removeClass('dkr-active');
                    $(this).toggleClass('dkr-active', (newRating != oldRating) && (newRating != 0));
                    parent.find('.dkr-rating').eq(0).text(newRating);
                    parent.find('.dkr-rating').toggleClass('dkr-positive', (newRating > oldRating) && (newRating != 0));
                    parent.find('.dkr-rating').toggleClass('dkr-negative', (newRating < oldRating) && (newRating != 0));
                }
             }, this)
         })
      });
});

$(document).on('show.bs.modal','#repostModal', function (e) {
    // Pass info about the post to the repost modal window
    var modal = $(this);
    var link = $(e.relatedTarget).data('link');
    $(e.currentTarget).find('#modalRepostButton').data('link', link);
})

$(function(){
    // Repost functionality
    $('#modalRepostButton').on('click', function(e){
        var repostBlogs = {'repost_blogs':[]};
        $("#formControlSelectBlogs>option:checked").each(function()
        {
            repostBlogs["repost_blogs"].push($(this).val());
        });
        //repostBlogs["csrfmiddlewaretoken"] = $('#csrf').val();
        var link = $('#modalRepostButton').data('link');
        var goto = $(this).data('go-to');
        $.ajax({
            type: 'POST',
            url: link,
            data: repostBlogs,
            success: function(response) {
                console.log('Success: ' + response);
                window.location = goto;
            }
        });
    });
});

$(function(){
    // Change post (hide, delete, publish)
    $('.dkr-change-post-link').on('click', function(e){
        var action = $(this).data('action');
        var link = $(this).data('link');
        var newval = $(this).data('newval');
        $.ajax({
            type: 'POST',
            url: link,
            context: this,
            data: {'action': action},
            success: function(response) {
                if (response['action'] == 'toggle') {
                    if (response['post_is_hidden']) {
                        $(this).html('Показать пост');
                    }
                    else {
                        $(this).html('Скрыть пост');
                    }
                }
                else {
                    $(this).html(newval);
                }
                console.log('Post changed successfully');
            }
        });
    });
});

$(function(){
    // Show reply to comment form
    $('.dkr-show-comment-reply-form').on('click', function(e){
        e.preventDefault();
        $(this).parents('.dkr-comment-block').eq(0).find('form').eq(0).toggle();
    });
});
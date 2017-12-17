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

$('#myModal').on('show.bs.modal', function (e) {
    console.log('asdsa');
    //get data-id attribute of the clicked element
    var bookId = $(e.relatedTarget).data('toggle');

    //populate the textbox
    $(e.currentTarget).find('input[id="recipient-name"]').val('dd');
    console.log('asdsa');

    var button = $(event.relatedTarget) // Button that triggered the modal
    var recipient = button.data('whatever') // Extract info from data-* attributes
    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    var modal = $(this)
    modal.find('.modal-title').text('New message to ' + recipient)
    modal.find('.modal-body input').val(recipient)
});
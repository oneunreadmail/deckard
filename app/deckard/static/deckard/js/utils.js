$(document).ready(function(){
    console.log("I'm ready!");  // Debug info
    if ($("#id_post_text").length) {
        var simplemde = new SimpleMDE({element: $("id_post_text")[0]});  // Markdown support for text areas
    }
    $('.dkr-login-link').popover();  // Popover login window enabled
    $('.dkr-login-link').on('click', function(e) {e.preventDefault(); return true;});  // Prevent scrolling to the top
});

// https://docs.djangoproject.com/en/2.0/ref/csrf/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // These HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    // Warning: there is no check for destination URL domain. Cookies and csrftoken header might possibly be sent to another domain.
    xhrFields: {
        withCredentials: true  // Allows sending cookies
    },
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));  // Easier CSRF protection, requires no template tag
        }

    }
});

$(function(){
    // Logout (POST request)
    $('#dkr-logout-link').on('click', function(e){
        var link = $(this).data('link');
        var goto = $(this).data('go-to');
        $.ajax({
            type: 'POST',
            url: link,
            success: function(response) {
                window.location = goto;
            }
        });
    });
});


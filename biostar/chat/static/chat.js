String.prototype.format = String.prototype.f = function () {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function room_view(uid) {

    let container = $('#chat-insert');


    $.ajax('/chat/room/' + uid + '/',{
        type: 'GET',
            dataType: 'json',
            data: {
            'uid':uid
            },
            success: function (data) {
            if (data.status === 'error'){

            }else{
                alert(container.html());
                container.html(data.html)
            }

            },
            error: function (xhr, status, text) {
                error_message($(this), xhr, status, text)
            }
    });

    container.html();
}


$(document).ready(function () {
      $(this).on('click', '.chat-room', function () {
        let uid = $(this).data('uid');
        room_view(uid)

    });
});
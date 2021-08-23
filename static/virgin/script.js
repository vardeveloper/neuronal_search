var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

$(window).load(function () {
    $messages.mCustomScrollbar();
    setTimeout(function () {
        fakeMessage("Haz tu pregunta.");
    }, 100);
});

function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
        scrollInertia: 10,
        timeout: 0
    });
}

function setDate() {
    d = new Date()
    if (m != d.getMinutes()) {
        m = d.getMinutes();
        $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
    }
}

function insertMessage() {
    msg = $('.message-input').val();
    if ($.trim(msg) == '') {
        return false;
    }
    let new_message_input = msg.replace(/simo|Simo|SImo/gi, function (x) {
      return x.toUpperCase();
    });

    console.info(new_message_input);

    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();
    setTimeout(function () {
        jinaMessage(new_message_input);
    }, 1000 + (Math.random() * 20) * 100);
}

$('.message-submit').click(function () {
    insertMessage();
});

$(window).on('keydown', function (e) {
    if (e.which == 13) {
        insertMessage();
        return false;
    }
})


function fakeMessage(msg) {
    if ($('.message-input').val() != '') {
        return false;
    }
    $('<div class="message loading new"><figure class="avatar"><img src="https://api.jina.ai/logo/logo-product/jina-core/logo-only/colored/Product%20logo_Core_Colorful%402x.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function () {
        $('.message.loading').remove();
        $('<div class="message new"><figure class="avatar"><img src="https://api.jina.ai/logo/logo-product/jina-core/logo-only/colored/Product%20logo_Core_Colorful%402x.png" /></figure>' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
        setDate();
        updateScrollbar();
    }, 200);
}


function jinaMessage(question) {
    if ($('.message-input').val() != '') {
        return false;
    }

    $('<div class="message loading new"><figure class="avatar"><img src="https://api.jina.ai/logo/logo-product/jina-core/logo-only/colored/Product%20logo_Core_Colorful%402x.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    $.ajax({
        type: "POST",
        url: $('#jina-server-addr').val() + "/search",
        data: JSON.stringify({"data": [question], "top_k": 3}),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
    }).success(function (data, textStatus, jqXHR) {
        console.info(data)
        var top_answer = data['data']['docs'][0]['matches'][0]
        $('.message.loading').remove();
        if (top_answer){
          $('<div class="message new">' +
              '<figure class="avatar">' +
              '<img src="https://api.jina.ai/logo/logo-product/jina-core/logo-only/colored/Product%20logo_Core_Colorful%402x.png" /></figure>' +
              '<div class="question">' + top_answer["text"] + '</div>' +
              top_answer["tags"]["answer"] +
              '</div>').appendTo($('.mCSB_container')).addClass('new');
        }
        else {
          $('<div class="message new">' +
              '<figure class="avatar">' +
              '<img src="https://api.jina.ai/logo/logo-product/jina-core/logo-only/colored/Product%20logo_Core_Colorful%402x.png" /></figure>' +
              '<div class="question">' + '</div>' +
              'Redefine tu pregunta por favor...' +
              '</div>').appendTo($('.mCSB_container')).addClass('new');
        }

        setDate();
        updateScrollbar();
    }).fail(function () {
        setTimeout(function () {
            fakeMessage("Connection failed, did you run <pre>Neural Search</pre> on local? Is your address <pre>" + $('#jina-server-addr').val() + "</pre> ?");
        }, 100);
    });
}
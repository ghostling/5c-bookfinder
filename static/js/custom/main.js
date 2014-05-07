function toggleLoading (div_id, action) {
    var parent = $(div_id);
    if (action == 'show') {
        $(div_id).append('<div id="loading"></div>');
        $('#loading').css({
            'position': 'absolute',
            'left': '0px',
            'top': '0px',
            'width': '100%',
            'height': '100%',
            'background-color': 'white',
            '-moz-opacity': '0.7',
            'opacity': '0.7',
            'filter': 'alpha(opacity=70)',
            'z-index': '90'
        });
        $('#loading').append('<img src="/static/images/spinner.gif" style="position: absolute; left: 35%; top: 35%">');
    } else if (action == "hide") {
        $('#loading').remove();
    }
};

var init = function() {
    $('#sign-up-form').submit(function(e) {
        e.preventDefault();
    });
    $('#sign-up-form').on('valid', function() {
        $.ajax({
            type: 'POST',
            url: '/signup',
            data: $('#sign-up-form').serialize(),
            beforeSend: function() {
                toggleLoading('#sign-up-modal', 'show');
            },
            complete: function() {
                toggleLoading('#sign-up-modal', 'hide');
            },
            success: function(data) {
                console.log(data);
                document.location.href= '/';
            },
            error: function(data) {
                console.log(data);
            },
        });
        return false;
    });
};

init();

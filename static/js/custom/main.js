var toggleLoading = function(div_id, action) {
    var parent = $(div_id);
    if (action == 'show') {
        console.log('going to add div');
        $(div_id).append('<div id="loading"></div>');
        console.log('added!');
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
        $('#loading').append('''<img src="/static/images/spinner.gif"
                             style="position: absolute; left: 35%; top: 35%">''');
    } else if (action == "hide") {

    }

};

var init = function() {
    $('#sign-up-form').submit(function() {
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
                alert(data);
            },
        });
        return false;
    });
};

init();

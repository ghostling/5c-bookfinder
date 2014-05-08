function postFormInModal(form_id, modal_id, post_url, redirect_url) {
    if (typeof(redirect_url) === 'undefined') {
        redirect_url = window.location.pathname;
    }

    $(form_id).submit(function(e) {
        e.preventDefault();
    });

    $(form_id).on('valid', function() {
        $.ajax({
            type: 'POST',
            url: post_url,
            data: $(form_id).serialize(),
            beforeSend: function() {
                toggleLoading(modal_id, 'show');
            },
            complete: function() {
                toggleLoading(modal_id, 'hide');
            },
            success: function(response) {
                document.location.href = redirect_url;
            },
            error: function(response) {
                console.log(response);
                error_message = response.responseText;
                addErrorMsgToDiv(modal_id, error_message);
            },
        });
        return false;
    });
} 

function toggleLoading(div_id, action) {
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
    } else if (action == 'hide') {
        $('#loading').remove();
    }
};

function addErrorMsgToDiv(div_id, msg) {
    $('#error-alert').remove();
    $(div_id).prepend('<div data-alert class="alert-box alert" id="error-alert">' 
                      + msg + '</div>');
};

function init() {
    /* Sign up form. */
    postFormInModal('#sign-up-form', '#sign-up-modal', '/signup', '/');

    /* Sign in form. */
    postFormInModal('#sign-in-form', '#sign-in-modal', '/signin', '/');
    
    /* Edit profile form. */
    postFormInModal('#edit-profile-form', '#edit-profile-modal', '/editprofile');
    
    /* Sell book form.*/
    postFormInModal('#sell-book-form', '#sell-book-modal', '/sellbook');

    $('.track-book').click(function(e) {
        link = $(this);
        e.preventDefault();
        $.ajax({
            url: '/wishlist',
            type: 'POST',
            data: {isbn: link.data('isbn')},
            success: function(response) {
                link.removeClass('track-book');
                link.addClass('untrack-book');
                child = link.children()[0];
                child.remove();
                link.append('<span class="label success">In Wishlist</span>');
            },
            error: function(response) {
                console.log(error); 
            }
        });
    });
    
    $('.untrack-book').click(function(e) {
        link = $(this);
        e.preventDefault();
        $.ajax({
            url: '/unwishlist',
            type: 'POST',
            data: {isbn: link.data('isbn')},
            success: function(response) {
                link.removeClass('untrack-book');
                link.addClass('track-book');
                child = link.children()[0];
                child.remove();
                link.append('<span class="label">Wishlist</span>');
            },
            error: function(response) {
                console.log(error); 
            }
        });
    });
};

init();

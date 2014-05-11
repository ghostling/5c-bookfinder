function postFormInModal(form_id, modal_id, post_url, redirect_url) {
    if (typeof(redirect_url) == 'undefined') {
        var redirect_url = window.location.pathname;
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
    // Sign up form.
    postFormInModal('#sign-up-form', '#sign-up-modal', '/signup', document.location.href);

    // Sign in form.
    postFormInModal('#sign-in-form', '#sign-in-modal', '/signin', document.location.href);
    
    // Edit profile form.
    postFormInModal('#edit-profile-form', '#edit-profile-modal', '/editprofile');
    
    // Sell book form.
    postFormInModal('#sell-book-form', '#sell-book-modal', '/sellbook');

    $('.wishlist-toggle').on('click', '.track-book', function(e) {
        console.log('tracked');
        // Create the new link node.
        var link = $(this);
        var linkParent = link.parent();
        var linkCopy = link.clone(false);


        e.preventDefault();
        $.ajax({
            url: '/wishlist',
            type: 'POST',
            data: {isbn: link.data('isbn')},
            success: function(response) {
                link.remove();
                linkCopy.removeClass('track-book');
                linkCopy.addClass('untrack-book');
                child = linkCopy.children()[0];
                child.remove();
                linkCopy.append('<span class="label success">In Wishlist</span>');
                linkParent.append(linkCopy);
            },
            error: function(response) {
                console.log(error); 
            }
        });
    });
    
    $('.wishlist-toggle').on('click', '.untrack-book', function(e) {
        console.log('untracked');
        // Create the new link node.
        var link = $(this);
        var linkParent = link.parent();
        var linkCopy = link.clone(false);


        e.preventDefault();
        $.ajax({
            url: '/unwishlist',
            type: 'POST',
            data: {isbn: link.data('isbn')},
            success: function(response) {
                link.remove();
                linkCopy.removeClass('untrack-book');
                linkCopy.addClass('track-book');
                child = linkCopy.children()[0];
                child.remove();
                linkCopy.append('<span class="label">Add to Wish List</span>');
                linkParent.append(linkCopy);
            },
            error: function(response) {
                console.log(error); 
            }
        });
    });

    // Passes data about a book into a modal to edit it.
    $('.edit-book').click(function(e) {
        var isbn = $(this).data('isbn');
        var title = $(this).data('title');
        var author = $(this).data('author');
        var price = $(this).data('price');
        var condition = $(this).data('condition');
        var edition = $(this).data('edition');
        var comments = $(this).data('comments');
        var createdAt = $(this).data('created-at');
        var listingId = $(this).data('listing-id');

        var modal = '#edit-book-modal';

        var heading = '';
        if (edition) {
            var heading = title + ' (' + edition + ' Ed.) by ' + author; 
        } else {
            var heading = title + ' by ' + author; 
        }

        $(modal + ' #edit-book-heading').text(heading);
        $(modal + ' #edit-book-isbn').text(isbn);
        $(modal + ' #edit-book-created-at').text(createdAt);
        $(modal + ' #edit-book-listing').val(listingId);
        $(modal + ' #edit-book-price').val(price);
        $(modal + ' #edit-book-comments').val(comments);
        var cond_val = $('#edit-condition option').filter(function() {
            return $(this).html() == condition;
        }).val();
        $('select').val(cond_val);
    });

    // Edit book form.
    postFormInModal('#edit-book-form', '#edit-book-modal', '/editbook');

    $('.delete-book').click(function(e) {
        var link = $(this);
        e.preventDefault();
        $.ajax({
            url: '/deletebook',
            type: 'POST',
            data: {listing_id: link.data('listingId')}, // somehow it renames listing-id to listingId
            success: function(response) {
                document.location.href = window.location.pathname;
            },
            error: function(response) {
                console.log(error); 
            }
        });
    });
    
    $('.sold-book').click(function(e) {
        var link = $(this);
        e.preventDefault();
        $.ajax({
            url: '/soldbook',
            type: 'POST',
            data: {listing_id: link.data('listingId')}, // somehow it renames listing-id to listingId
            success: function(response) {
                document.location.href = window.location.pathname;
            },
            error: function(response) {
                console.log(error); 
            }
        });
    });
};

init();

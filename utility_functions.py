import config
import hashlib
import hmac
import json
import random
import requests
import string


GOOGLE_BOOKS_API_BASE_URL = 'https://www.googleapis.com/books/v1/volumes?q={0}'

# TODO: Cache this response so that we don't have to fetch it everytime!
def get_google_image_for_book(isbn):
    # Get the content and parse the JSON response.
    r = requests.get(GOOGLE_BOOKS_API_BASE_URL.format(isbn))
    response = json.loads(r.text)

    # Get the first item in the list and hope that's the right one.
    book = response['items'][0]

    return book['volumeInfo']['imageLinks']['thumbnail']

# Used in cookie to maintain login status
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(config.SECRET, str(val)).hexdigest())

# Used to check cookie.
def check_secure_val(secure_val):
    sec_val = secure_val.split('|')[0]
    if sec_val == make_secure_val(val):
        return sec_val
 
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(8))

def make_pw_hash(email, pw, salt=''):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(email + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def validate_login(email, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(email, pw, salt)

def set_logged_in_user_session(uid, name):
    session['user_hash'] = make_secure_val(uid+name)
    session['uid'] = uid
    session['user_name'] = name

def check_valid_user_session(session):
    return session['user_hash'] == make_secure_val(session['uid'] 
            + session['user_name'])

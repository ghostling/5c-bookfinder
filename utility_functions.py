import random
import hmac
import hashlib
import string

SECRET = 'temporary secret that is not a secret yay'

# Used in cookie to maintain login status
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(SECRET, str(val)).hexdigest())

# Used to check cookie.
def check_secure_val(secure_val):
    sec_val = secure_val.split('|')[0]
    if sec_val == make_secure_val(val):
        return sec_val
 
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(8))

def make_pw_hash(email, pw, salt=""):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(email + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def validate_login(email, pw, h):
    salt = h.split(',')[1]
    return h == make_pw_hash(email, pw, salt)

def set_logged_in_user_session(user_id, name):
    session['user_hash'] = make_secure_val(user_id+name)
    session['user_id'] = user_id
    session['user_name'] = name

def check_valid_user_session(session):
    return session['user_hash'] == make_secure_val(session['user_id'] 
            + session['user_name'])

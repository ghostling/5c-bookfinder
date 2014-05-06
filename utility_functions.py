import random
import hmac
import hashlib

SECRET = 'temporary secret that is not a secret yay'

# Used in cookie to maintain login status
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(SECRET, str(val)).hexdigest())

# Used to check cookie.
def check_secure_val(secure_pw):
    sec_pw = secure_pw.split('|')[0]
    if sec_pw == make_secure_pw(pw):
        return sec_pw
 
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

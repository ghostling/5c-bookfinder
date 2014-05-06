from flask import Flask, render_template, redirect, session
import utility_functions as UF
import MySQLdb, MySQLdb.cursors
import json
import requests

# Declare globals.
BOOK_CONDITION = {
    1: 'New',
    2: 'Like New',
    3: 'Very Good',
    4: 'Good',
    5: 'Acceptable'
}
GOOGLE_BOOKS_API_BASE_URL = 'https://www.googleapis.com/books/v1/volumes?q={0}'

app = Flask(__name__)

def get_db_cursor():
    # Easier to access db and cursor.
    db = MySQLdb.connect(host='localhost', port=3306, user='5cbookfinder',
            passwd='g4G5IkDOM3a91EV', db='5cbookfinder', 
            cursorclass=MySQLdb.cursors.DictCursor)
    return db.cursor()



@app.route('/')
def index():
    return render_template('index.html')

# TODO: Cache this response so that we don't have to fetch it everytime!
def get_google_image_for_book(isbn):
    # Get the content and parse the JSON response.
    r = requests.get(GOOGLE_BOOKS_API_BASE_URL.format(isbn))
    response = json.loads(r.text)

    # Get the first item in the list and hope that's the right one.
    book = response["items"][0]

    return book["volumeInfo"]["imageLinks"]["thumbnail"]

@app.route('/user/<userid>')
def get_user_profile(userid):
    # Get a cursor.
    cursor = get_db_cursor()

    # Sanitize user input.
    try:
        userid = str(int(MySQLdb.escape_string(userid)))
    except ValueError:
        raise Exception

    # Select the right user and raise an error if we don't have an exact match.
    cursor.execute('SELECT * FROM Users WHERE user_id = %s', userid)
    rows_affected = cursor.rowcount
    user = cursor.fetchone()
    if int(rows_affected) is not 1:
        raise Exception

    # Get the books that we've recently listed.
    recently_listed = []
    cursor.execute('SELECT * FROM BooksForSale B ORDER BY updated_at DESC LIMIT 10')
    recently_listed = cursor.fetchall()

    # Get the books that are currently being sold that are on their wishlist.
    cursor.execute("""SELECT B.*, BFS.created_at, BFS.price, BFS.book_condition, 
        USB.user_id AS 'owner_id', U.name AS 'owner'
        FROM Books B, UserTracksBook UTB, BooksForSale BFS, UserSellsBook USB, Users U
        WHERE UTB.book_isbn = B.book_isbn AND BFS.book_isbn = B.book_isbn
        AND BFS.status = 1 AND U.user_id = USB.user_id AND UTB.user_id = %s""", userid)
    wishlist_selling = cursor.fetchall()

    # Then, get the books that they themselves are selling.
    cursor.execute("""SELECT BFS.*, B.* 
        FROM BooksForSale BFS, Books B, UserSellsBook USB
        WHERE  B.book_isbn = BFS.book_isbn AND USB.listing_id = BFS.listing_id AND 
        USB.user_id = %s""", userid)
    user_selling = cursor.fetchall()

    # Prepare the URL for Input
    for book in wishlist_selling:
        book['img_url'] = get_google_image_for_book(book['book_isbn'])
        book['book_condition'] = BOOK_CONDITION[book['book_condition']]

    for book in user_selling:
        book['img_url'] = get_google_image_for_book(book['book_isbn'])
        book['book_condition'] = BOOK_CONDITION[book['book_condition']]

    cursor.close()

    return render_template('user_profile.html', wishlist_selling=wishlist_selling, user_selling=user_selling, user=user)

@app.route('/book/<isbn>')
def get_book_information(isbn):
    return render_template('book.html')

@app.route('/course/<course_number>')
def get_course_information(course_number):
    return render_template('course.html')

@app.route('/search')
def get_search_json():
    return 'Hello, world!'

@app.route('/signup', methods=['POST'])
def signup(email, name, phone_number, pw):
    # Get a cursor.
    cursor = get_db_cursor()

    if request.method =='POST':
        # Valid email not in use.
        cursor.execute('SELECT * FROM Users WHERE email_address = %s', email)
        user = cursor.fetchall()

        if not user:
            hashed_pw = UF.make_pw_hash(email, pw)

            cursor.execute('INSERT INTO Users VALUES (%s, %s, %s, %s)',
                    (name, email, hash_pw, phone_number))
            db.commit()

            # Set session to save user login status.
            session['user_id'] = UF.make_secure_val(email)
            return redirect(url_for('/'))
        else:
            # TODO: Fix this.
            return {'signup_error': 'This email is already in use.'}

@app.route('/login', methods=['POST'])
def login(email, pw):
    # Get a cursor.
    cursor = get_db_cursor()

    if request.method == 'POST':
        # Get account associated with email.
        cursor.execute('SELECT * FROM Users WHERE email_address = %s', email)
        user = cursor.fetchall()

        if user:
            salt = user.hashed_password.split(',')[1]
            if user.hashed_password == UF.make_pw_hash(email, pw, salt):
                session['user_id'] = UF.make_secure_val(email)
                return redirect(url_for('/'))
        else:
            # TODO: Fix this.
            return {'login_error': 'Either email or password is incorrect.'}

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('/'))

if __name__ == '__main__':
    app.run(debug=True)

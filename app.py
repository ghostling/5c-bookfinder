from flask import Flask, render_template, redirect, session, request, url_for, Response, make_response
import utility_functions as UF
import MySQLdb, MySQLdb.cursors
import json
import requests
import config
import datetime

# TODO: Every time you use session['user_id'], you should check it with the
# user hash....

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
app.secret_key = config.SECRET_KEY

def get_db_cursor():
    # Easier to access db and cursor.
    # db = MySQLdb.connect(host='localhost', port=3306, user='5cbookfinder',
    #         passwd='g4G5IkDOM3a91EV', db='5cbookfinder',
    #         cursorclass=MySQLdb.cursors.DictCursor)
    db = MySQLdb.connect(host='bookfinder.5capps.com', port=3306, user='5cbookfinder',
             passwd='g4G5IkDOM3a91EV', db='5cbookfinder',
             cursorclass=MySQLdb.cursors.DictCursor)

    return db, db.cursor()

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
    db, cursor = get_db_cursor()

    # Sanitize user input.
    try:
        userid = str(int(MySQLdb.escape_string(userid)))
    except ValueError:
        raise Exception

    # Select the right user and raise an error if we don't have an exact match.
    cursor.execute('SELECT * FROM Users WHERE user_id = %s', (userid,))
    rows_affected = cursor.rowcount
    user = cursor.fetchone()
    if int(rows_affected) is not 1:
        raise Exception

    # Get the books that we've recently listed.
    recently_listed = []
    cursor.execute('SELECT * FROM BooksForSale B ORDER BY updated_at DESC LIMIT 10')
    recently_listed = cursor.fetchall()

    # Get the books that are currently being sold that are on their wishlist.
    # TODO: Something wrong with this query...duplicate results.
    cursor.execute('''SELECT B.*, BFS.created_at, BFS.price, BFS.book_condition,
        USB.user_id AS 'owner_id', U.name AS 'owner'
        FROM Books B, UserTracksBook UTB, BooksForSale BFS, UserSellsBook USB, Users U
        WHERE UTB.book_isbn = B.book_isbn AND BFS.book_isbn = B.book_isbn
        AND BFS.status = 1 AND U.user_id = USB.user_id AND UTB.user_id = %s''', (userid,))
    wishlist_selling = cursor.fetchall()

    # Then, get the books that they themselves are selling.
    cursor.execute('''SELECT BFS.*, B.*
        FROM BooksForSale BFS, Books B, UserSellsBook USB
        WHERE  B.book_isbn = BFS.book_isbn AND USB.listing_id = BFS.listing_id AND
        USB.user_id = %s''', (userid,))
    user_selling = cursor.fetchall()

    # Prepare the image URL and book_condition.
    for book in wishlist_selling:
        book['img_url'] = get_google_image_for_book(book['book_isbn'])
        book['book_condition'] = BOOK_CONDITION[book['book_condition']]

    for book in user_selling:
        book['img_url'] = get_google_image_for_book(book['book_isbn'])
        book['book_condition'] = BOOK_CONDITION[book['book_condition']]

    cursor.close()

    return render_template('user_profile.html', wishlist_selling=wishlist_selling, user_selling=user_selling, user=user, condition = BOOK_CONDITION)

@app.route('/book/<isbn>')
def get_book_information(isbn):
    db, cursor = get_db_cursor()

    cursor.execute('SELECT * FROM Books WHERE book_isbn=%s', (isbn,))
    book = cursor.fetchone()

    cursor.execute('''SELECT C.course_number, C.title FROM
            CourseRequiresBook CRB, Courses C WHERE CRB.book_isbn=%s AND
            CRB.course_number=C.course_number''', (isbn,))
    book['req_by_list'] = cursor.fetchall()

    cursor.execute('''SELECT C.course_number, C.title FROM
            CourseRecommendsBook CRB, Courses C WHERE CRB.book_isbn=%s AND
            CRB.course_number=C.course_number''', (isbn,))
    book['rec_by_list'] = cursor.fetchall()

    cursor.execute('''SELECT B.price, B.book_condition, B.comments, U.user_id,
            UU.name, B.updated_at FROM BooksForSale B, UserSellsBook U,
            Users UU WHERE B.book_isbn=%s AND B.listing_id=U.listing_id AND
            U.user_id=UU.user_id''', (isbn,))
    book['selling_list'] = cursor.fetchall()
    for b in book['selling_list']:
        b['updated_at'] = b['updated_at'].strftime('%m/%d/%Y')
        b['book_condition'] = BOOK_CONDITION[b['book_condition']]

    # Prepare the image URL.
    book['img_url'] = get_google_image_for_book(book['book_isbn'])

    return render_template('book.html', book=book)

@app.route('/course/<course_number>')
def get_course_information(course_number):
    # Get a cursor.
    db, cursor = get_db_cursor()

    user_id = session['user_id']

    cursor.execute('SELECT * FROM Courses WHERE course_number = %s', (course_number,))
    course = cursor.fetchone()

    cursor.execute('''SELECT B.author, B.book_isbn, B.title, B.edition FROM
            CourseRequiresBook CRB, Books B
            WHERE CRB.course_number = %s
            AND B.book_isbn = CRB.book_isbn''', (course_number,))
    books_required = cursor.fetchall()

    for b in books_required:
        cursor.execute('''SELECT * FROM BooksForSale WHERE book_isbn=%s''',
                (b['book_isbn'],))
        b['number_selling'] = cursor.rowcount

        # Check if in current user's wishlist.
        cursor.execute('''SELECT * FROM UserTracksBook WHERE user_id=%s AND
                book_isbn=%s''', (user_id, b['book_isbn'],))
        if cursor.rowcount == 1:
            b['in_user_wishlist'] = True

    cursor.execute('''SELECT B.author, B.book_isbn, B.title, B.edition FROM
            CourseRecommendsBook CRB, Books B
            WHERE CRB.course_number = %s
            AND B.book_isbn = CRB.book_isbn''', (course_number,))
    books_recommended = cursor.fetchall()

    for b in books_recommended:
        cursor.execute('''SELECT * FROM BooksForSale WHERE book_isbn=%s''',
                (b['book_isbn'],))
        b['number_selling'] = cursor.rowcount

        # Check if in current user's wishlist.
        cursor.execute('''SELECT * FROM UserTracksBook WHERE user_id=%s AND
                book_isbn=%s''', (user_id, b['book_isbn'],))
        if cursor.rowcount == 1:
            b['in_user_wishlist'] = True

    return render_template('course.html', course=course,
            books_required=books_required, books_recommended=books_recommended)

@app.route('/sellbook', methods=['POST'])
def sellbook():
    db, cursor = get_db_cursor()

    if request.method == 'POST':
        isbn = str(request.form['isbn'])
        price = str(request.form['price'])
        condition = str(request.form['condition'])
        comments = str(request.form['comments'])
        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_id = session['user_id']

        # Check if any course req/rec's this book.
        cursor.execute('''SELECT * FROM CourseRequiresBook RQ, CourseRecommendsBook RC
                WHERE RQ.book_isbn=%s OR RC.book_isbn=%s''', (isbn, isbn,))
        valid_course_book = cursor.fetchone()

        if not valid_course_book:
            return make_response('''This book is not required or recommended by
                    this course. If this is not true, please fill out the other
                    form.''', 400)
        if float(price) < 0:
            return make_response('You cannot have a negative price!', 400)
        else:
            cursor.execute('''INSERT INTO BooksForSale (book_isbn, status,
                    created_at, price, book_condition, comments) VALUES
                    (%s, %s, %s, %s, %s, %s)''', (isbn, 1, created_at,
                    price, condition, comments,))
            listing_id = db.insert_id()
            cursor.execute('''INSERT INTO UserSellsBook VALUES (%s, %s)''',
                    (user_id, listing_id,))
            db.commit()

        return make_response('', 200)

@app.route('/wishlist', methods=['POST'])
def add_to_wishlist():
    db, cursor = get_db_cursor()

    if request.method == 'POST':
        isbn = str(request.form['isbn'])
        user_id = session['user_id']

        cursor.execute('''INSERT INTO UserTracksBook VALUES (%s, %s)''',
                (user_id, isbn,))
        db.commit()

        # TODO: What could possibly go wrong...? (Serious question.)
        return make_response('', 200)

@app.route('/unwishlist', methods=['POST'])
def remove_from_wishlist():
    db, cursor = get_db_cursor()

    if request.method == 'POST':
        isbn = str(request.form['isbn'])
        user_id = session['user_id']

        cursor.execute('''DELETE FROM UserTracksBook WHERE user_id=%s AND
                book_isbn=%s''', (user_id, isbn,))
        db.commit()

        # TODO: What could possibly go wrong...? (Serious question.)
        return make_response('', 200)

@app.route('/search')
def get_search_json():
    return 'Hello, world!'

@app.route('/signup', methods=['POST'])
def signup():
    # Get a cursor.
    db, cursor = get_db_cursor()

    if request.method == 'POST':
        name = str(request.form['name'])
        email = str(request.form['email'])
        phone_number = str(request.form['phone_number'])
        password = str(request.form['password'])

        # Valid email not in use.
        cursor.execute('SELECT * FROM Users WHERE email_address = %s', (email,))
        user = cursor.fetchall()

        if not user:
            hashed_pw = UF.make_pw_hash(email, password)

            cursor.execute('''INSERT INTO Users
                    (name, email_address, hashed_password, phone_number)
                    VALUES (%s, %s, %s, %s)''',
                    (name, email, hashed_pw, phone_number,))
            user_id = db.insert_id()
            db.commit()

            # Set session to save user login status.
            set_logged_in_user_session(user_id, name)
            return make_response('', 200)
        else:
            return make_response('Email already in use.', 400)

    return json.dumps(response)

@app.route('/signin', methods=['POST'])
def signin():
    # Get a cursor.
    db, cursor = get_db_cursor()

    if request.method == 'POST':
        email = str(request.form['email'])
        password = str(request.form['password'])

        # Get account associated with email.
        cursor.execute('SELECT * FROM Users WHERE email_address = %s', (email,))
        user = cursor.fetchone()

        if user:
            salt = user['hashed_password'].split(',')[1]
            if user['hashed_password'] == UF.make_pw_hash(email, password, salt):
                set_logged_in_user_session(user['user_id'], user['name'])
                return make_response('', 200)

        # Whether user doesn't exists or password mismatch, we want one error.
        return make_response('The email or password is incorrect.', 400)

def set_logged_in_user_session(user_id, name):
    session['user_hash'] = UF.make_secure_val(user_id)
    session['user_id'] = user_id
    session['user_name'] = name

@app.route('/editprofile', methods=['POST'])
def edit_profile():
    db, cursor = get_db_cursor()

    if request.method == 'POST':
        name = str(request.form['name'])
        email = str(request.form['email'])
        phone_number = str(request.form['phone_number'])

        # Check if user is allowed to edit this profile.
        if session['user_hash'] == UF.make_secure_val(session['user_id']):
            cursor.execute('SELECT * FROM Users WHERE user_id = %s', (str(session['user_id']),))
            cur_user = cursor.fetchone()
            # Check if email is already in use.
            cursor.execute('SELECT * FROM Users WHERE email_address = %s', (email,))
            user = cursor.fetchone()
            if (not user) or (user and (email == cur_user['email_address'])):
                cursor.execute('''UPDATE Users SET name=%s, email_address=%s,
                        phone_number=%s WHERE user_id=%s''', (name, email,
                        phone_number, session['user_id']))
                db.commit()
                return make_response('', 200)
            else:
                return make_response('This email is already in use.', 400)
        else:
            session.clear()
            return make_response('You are not allowed to edit this profile.', 400)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

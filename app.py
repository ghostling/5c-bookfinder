from flask import Flask, render_template, redirect, session, request, url_for, Response, make_response, abort
import MySQLdb, MySQLdb.cursors
import config
import datetime
import utility_functions as UF


app = Flask(__name__)
app.secret_key = config.SECRET_KEY

def get_db_cursor():
    # Easier to access db and cursor.
    db = MySQLdb.connect(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER,
             passwd=config.DB_PASSWD, db=config.DB,
             cursorclass=MySQLdb.cursors.DictCursor)

    return db, db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

def get_book_condition_options():
    # Get a cursor.
    db, cursor = get_db_cursor()

    cursor.execute('SELECT * FROM BookCondition ORDER BY rating DESC')
    result = cursor.fetchall()

    db.close()

    return result

def add_book_condition(book):
    # Get the book condition options.
    condition_options = get_book_condition_options()
    index = 0

    for option in condition_options:
        if book['rating'] is option['rating']:
            index = condition_options.index(option)
            break

    book['condition_desc'] = condition_options[index]['description']

    return book

@app.route('/user/<uid>')
def get_user_profile(uid):
    # Get a cursor.
    db, cursor = get_db_cursor()

    # Sanitize user input.
    try:
        uid = str(int(MySQLdb.escape_string(uid)))
    except ValueError:
        abort(404)

    # Select the right user and raise an error if we don't have an exact match.
    cursor.execute('SELECT * FROM Users WHERE uid = %s', (uid,))
    rows_affected = cursor.rowcount
    user = cursor.fetchone()
    if int(rows_affected) is not 1:
        abort(404)

    # Check if they have anything in their wishlist.
    cursor.execute('SELECT * FROM UserTracksBook WHERE uid = %s', (uid,))
    if cursor.rowcount > 0:
        has_wishlist_items = True
    else:
        has_wishlist_items = False

    # Get the books that are currently on their wishlist.
    cursor.execute('''SELECT B.* FROM UserTracksBook UTB, Books B WHERE
            UTB.uid=%s AND UTB.isbn=B.isbn''', (uid,))
    wishlist = cursor.fetchall()

    # Get how many books are on the list:
    for b in wishlist:
        cursor.execute('''SELECT * FROM BooksForSale WHERE isbn=%s''',
                (b['isbn'],))
        b['number_selling'] = cursor.rowcount

    # Then, get the books that they themselves are selling.
    cursor.execute('''SELECT BFS.*, B.*
        FROM BooksForSale BFS, Books B
        WHERE  B.isbn = BFS.isbn AND BFS.seller_id = %s AND BFS.status = 1''', (uid,))
    user_selling = cursor.fetchall()

    # Prepare the image URL and book_condition.
    for book in wishlist:
        # Set the image.
        book['img_url'] = UF.get_google_image_for_book(book['isbn'])

    for book in user_selling:
        # Set the image.
        book['img_url'] = UF.get_google_image_for_book(book['isbn'])

        # Add book condition.
        book = add_book_condition(book)

    cursor.close()

    return render_template('user_profile.html', wishlist=wishlist, \
        user_selling=user_selling, user=user, condition_options=get_book_condition_options(), \
        has_wishlist_items=has_wishlist_items)

@app.route('/book/<isbn>')
def get_book_information(isbn):
    db, cursor = get_db_cursor()

    # Check if they're signed in to display the offer to sell that book.
    if UF.check_valid_user_session(session):
        uid = session.get('uid')
        logged_in = True
    else:
        logged_in = False

    cursor.execute('SELECT * FROM Books WHERE isbn = %s', (isbn,))

    # Check if the ISBN is valid.
    if int(cursor.rowcount) < 1:
        abort(404)

    book = cursor.fetchone()

    # Get the required books.
    cursor.execute('''SELECT C.course_number, C.title FROM
            CourseRequiresBook CRB, Courses C WHERE CRB.isbn = %s AND
            CRB.course_number = C.course_number''', (isbn,))
    book['req_by_list'] = cursor.fetchall()

    # Get the recommended books.
    cursor.execute('''SELECT C.course_number, C.title FROM
            CourseRecommendsBook CRB, Courses C WHERE CRB.isbn = %s AND
            CRB.course_number = C.course_number''', (isbn,))
    book['rec_by_list'] = cursor.fetchall()

    # Get all of the books that are being sold.
    cursor.execute('''SELECT B.*, U.name
        FROM BooksForSale B, Users U
        WHERE B.isbn = %s AND B.seller_id = U.uid AND B.status = 1''', (isbn,))
    book['selling_list'] = cursor.fetchall()

    # Add the appropriate information.
    for b in book['selling_list']:
        b['updated_at'] = b['updated_at'].strftime('%m/%d/%Y')
        b = add_book_condition(b)

    # Prepare the image URL.
    book['img_url'] = UF.get_google_image_for_book(book['isbn'])

    return render_template('book.html', book=book, \
        condition_options=get_book_condition_options(), logged_in=logged_in)

@app.route('/course/<course_number>')
def get_course_information(course_number):
    # Get a cursor.
    db, cursor = get_db_cursor()

    if UF.check_valid_user_session(session):
        uid = session.get('uid')
        logged_in = True
    else:
        uid = None
        logged_in = False

    cursor.execute('SELECT * FROM Courses WHERE course_number = %s', (course_number,))

    # Check if the course number is valid.
    if int(cursor.rowcount) < 1:
        abort(404)

    course = cursor.fetchone()

    # Get the course's required books.
    cursor.execute('''SELECT B.* FROM CourseRequiresBook CRB, Books B
            WHERE CRB.course_number = %s AND B.isbn = CRB.isbn''', (course_number,))
    books_required = cursor.fetchall()

    # Process the required books.
    for b in books_required:
        cursor.execute('''SELECT * FROM BooksForSale WHERE isbn = %s AND status = 1''',
                (b['isbn'],))
        b['number_selling'] = cursor.rowcount

        # Check if in current user's wishlist only if they're logged in.
        if uid:
            cursor.execute('''SELECT * FROM UserTracksBook WHERE uid = %s AND
                    isbn = %s''', (uid, b['isbn'],))
            if cursor.rowcount == 1:
                b['in_user_wishlist'] = True

    # Get the course's recommended books.
    cursor.execute('''SELECT B.* FROM
            CourseRecommendsBook CRB, Books B
            WHERE CRB.course_number = %s AND B.isbn = CRB.isbn''', (course_number,))
    books_recommended = cursor.fetchall()

    # Process the recommended books.
    for b in books_recommended:
        cursor.execute('''SELECT * FROM BooksForSale WHERE isbn = %s AND status = 1''',
                (b['isbn'],))
        b['number_selling'] = cursor.rowcount

        # Check if in current user's wishlist only if they're logged in:
        if uid:
            cursor.execute('''SELECT * FROM UserTracksBook WHERE uid = %s AND
                    isbn = %s''', (uid, b['isbn'],))
            if cursor.rowcount == 1:
                b['in_user_wishlist'] = True

    return render_template('course.html', course=course,
            books_required=books_required, books_recommended=books_recommended, logged_in=logged_in)

@app.route('/sellbook', methods=['POST'])
def sell_book():
    db, cursor = get_db_cursor()

    if request.method == 'POST' and UF.check_valid_user_session(session):
        isbn = str(request.form['isbn'])
        price = str(request.form['price'])
        condition = str(request.form['condition'])
        comments = str(request.form['comments'])
        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        uid = session['uid']

        # Check if any course req/rec's this book.
        cursor.execute('''SELECT * FROM CourseRequiresBook RQ, CourseRecommendsBook RC
                WHERE RQ.isbn = %s OR RC.isbn = %s''', (isbn, isbn,))
        valid_course_book = cursor.fetchone()

        if not valid_course_book:
            return make_response('''This book is not required or recommended by
                    this course. If this is not true, please fill out the other
                    form.''', 400)
        if float(price) < 0:
            return make_response('You cannot have a negative price!', 400)
        else:
            cursor.execute('''INSERT INTO BooksForSale (isbn, seller_id, status,
                    created_at, price, rating, comments) VALUES
                    (%s, %s, %s, %s, %s, %s, %s)''', (isbn, uid, 1, created_at, \
                    price, condition, comments,))
            db.commit()

        return make_response('', 200)
    else:
        session.clear()
        return make_response('You are not authorized to sell a book.', 401)

@app.route('/editbook', methods=['POST'])
def edit_book():
    db, cursor = get_db_cursor()

    if request.method == 'POST' and UF.check_valid_user_session(session):
        listing_id = str(request.form['listing_id'])
        price = str(request.form['price'])
        condition = str(request.form['condition'])
        comments = str(request.form['comments'])
        uid = session['uid']

        # Check if user is allowed to edit this listing.
        cursor.execute('''SELECT * FROM BooksForSale WHERE seller_id=%s AND
                listing_id=%s''', (uid, listing_id,))
        if not cursor.fetchone():
            return make_response('You are not allowed to edit this book!', 200)

        if float(price) < 0:
            return make_response('You cannot have a negative price!', 400)
        else:
            cursor.execute('''UPDATE BooksForSale SET price=%s, rating=%s,
                    comments=%s WHERE listing_id=%s''', (price, condition,
                    comments, listing_id, ))
            db.commit()

        return make_response('', 200)
    else:
        session.clear()
        return make_response('You are not authorized to sell a book.', 401)

def change_book_status(listing_id, status):
    db, cursor = get_db_cursor()
    uid = session['uid']

    # Check if user is allowed to edit this listing.
    cursor.execute('''SELECT * FROM BooksForSale WHERE seller_id=%s AND
            listing_id=%s''', (uid, listing_id,))
    if not cursor.fetchone():
        return make_response('You are not allowed to edit this book!', 401)
    else:
        cursor.execute('''UPDATE BooksForSale SET status=%s WHERE
                listing_id=%s''', (status, listing_id,))
        db.commit()
    return make_response('', 200)

@app.route('/deletebook', methods=['POST'])
def delete_book():
    if request.method == 'POST' and UF.check_valid_user_session(session):
        listing_id = str(request.form['listing_id'])
        status = 0 # Inactive
        return change_book_status(listing_id, status)
    else:
        session.clear()
        return make_response('You are not authorized to change this book status.', 401)

@app.route('/soldbook', methods=['POST'])
def sold_book():
    if request.method == 'POST' and UF.check_valid_user_session(session):
        listing_id = str(request.form['listing_id'])
        status = 2 # Inactive
        return change_book_status(listing_id, status)
    else:
        session.clear()
        return make_response('You are not authorized to change this book status.', 401)

@app.route('/wishlist', methods=['POST'])
def add_to_wishlist():
    db, cursor = get_db_cursor()

    if request.method == 'POST' and UF.check_valid_user_session(session):
        isbn = str(request.form['isbn'])
        uid = session['uid']

        cursor.execute('''INSERT INTO UserTracksBook VALUES (%s, %s)''',
                (uid, isbn,))
        db.commit()

        return make_response('', 200)
    else:
        session.clear()
        return make_response('', 401)

@app.route('/unwishlist', methods=['POST'])
def remove_from_wishlist():
    db, cursor = get_db_cursor()

    if request.method == 'POST' and UF.check_valid_user_session(session):
        isbn = str(request.form['isbn'])
        uid = session['uid']

        cursor.execute('''DELETE FROM UserTracksBook WHERE uid = %s AND
                isbn = %s''', (uid, isbn,))
        db.commit()

        return make_response('', 200)
    else:
        session.clear()
        return make_response('', 401)

@app.route('/signup', methods=['POST'])
def signup():
    # Get a cursor.
    db, cursor = get_db_cursor()

    if request.method == 'POST':
        name = str(request.form['name'])
        email = str(request.form['email'])
        phone = str(request.form['phone_number'])
        password = str(request.form['password'])

        # Make sure that the e-mail address given is valid.
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email, ))
        user = cursor.fetchall()

        if not user:
            hashed_pw = UF.make_pw_hash(email, password)

            cursor.execute('''INSERT INTO Users
                    (name, email, hashed_pw, phone)
                    VALUES (%s, %s, %s, %s)''',
                    (name, email, hashed_pw, phone,))
            uid = db.insert_id()
            db.commit()

            # Set session to save user login status.
            session = UF.set_logged_in_user_session(uid, name)
            return make_response('', 200)
        else:
            return make_response('Email already in use.', 400)

@app.route('/signin', methods=['POST'])
def signin():
    # Get a cursor.
    db, cursor = get_db_cursor()

    if request.method == 'POST':
        email = str(request.form['email'])
        password = str(request.form['password'])

        # Get account associated with email.
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            salt = user['hashed_pw'].split(',')[1]
            if user['hashed_pw'] == UF.make_pw_hash(email, password, salt):
                session = UF.set_logged_in_user_session(user['uid'], user['name'])
                return make_response('', 200)

        # Whether user doesn't exists or password mismatch, we want one error.
        return make_response('The email or password is incorrect.', 400)

@app.route('/editprofile', methods=['POST'])
def edit_profile():
    db, cursor = get_db_cursor()

    if request.method == 'POST' and UF.check_valid_user_session(session):
        name = str(request.form['name'])
        email = str(request.form['email'])
        phone = str(request.form['phone_number'])
        uid = session['uid']

        cursor.execute('SELECT * FROM Users WHERE uid = %s', (str(uid),))
        cur_user = cursor.fetchone()
        # Check if email is already in use.
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        user = cursor.fetchone()
        if (not user) or (user and (email == cur_user['email'])):
            cursor.execute('''UPDATE Users SET name = %s, email = %s,
                    phone = %s WHERE uid = %s''', (name, email,
                    phone, uid))
            db.commit()
            return make_response('', 200)
        else:
            return make_response('This email is already in use.', 400)
    else:
        session.clear()
        return make_response('You are not authorized to edit this profile.', 401)

@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

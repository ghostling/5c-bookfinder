from flask import Flask, render_template, redirect, session
import utility_functions as UF
import MySQLdb, MySQLdb.cursors

app = Flask(__name__)

class MainDB():
    # Easier to access db and cursor.
    db = MySQLdb.connect(host='localhost', port=3306, user='5cbookfinder',
            passwd='g4G5IkDOM3a91EV', db='5cbookfinder', 
            cursorclass=MySQLdb.cursors.DictCursor)
    cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<userid>')
def get_user_profile(userid):
    # Sanitize user input.
    try:
        userid = str(int(MySQLdb.escape_string(userid)))
    except ValueError:
        raise Exception

    # Select the right user and raise an error if we don't have an exact match.
    MainDB.cursor.execute('SELECT user_id FROM Users WHERE user_id = %s', userid)
    rows_affected = cursor.rowcount
    if int(rows_affected) is not 1:
        raise Exception

    # Otherwise, get the books they track and sell.
    #cursor.execute('SELECT B.* FROM Books B INNER JOIN UserTracksBook UTB ON UTB.book_isbn = B.book_isbn WHERE UTB.user_id = %s', userid)
    #tracked_books = cursor.fetchall()

    MainDB.cursor.execute('SELECT BFS.listing_id, BFS.book_isbn, BFS.created_at, BFS.edition, BFS.price, BFS.book_condition, B.*  FROM BooksForSale BFS, Books B, UserSellsBook USB WHERE B.book_isbn = BFS.book_isbn AND USB.listing_id = BFS.listing_id AND USB.user_id = %s', userid)
    selling_books = cursor.fetchall()

    # Books we're tracking
    #for b in tracked_books:

    # Books we're selling.

    # Get the book image from Google Books API.


    db.close()

    return render_template('user_profile.html')

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
    if request.method =='POST':
        # Valid email not in use.
        MainDB.cursor.execute('SELECT * FROM Users WHERE email_address = %s', email)
        user = MainDB.cursor.fetchall()

        if not user:
            hashed_pw = UF.make_pw_hash(email, pw)

            MainDB.cursor.execute('INSERT INTO Users VALUES (%s, %s, %s, %s)',
                    (name, email, hash_pw, phone_number))
            MainDB.db.commit()

            # Set session to save user login status.
            session['user_id'] = UF.make_secure_val(email)
            return redirect(url_for('/'))
        else:
            # TODO: Fix this.
            return {'signup_error': 'This email is already in use.'}

@app.route('/login', methods=['POST'])
def login(email, pw):
    if request.method == 'POST':
        # Get account associated with email.
        MainDB.cursor.execute('SELECT * FROM Users WHERE email_address = %s', email)
        user = MainDB.cursor.fetchall()

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

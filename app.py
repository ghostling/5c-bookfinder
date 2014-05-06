from flask import Flask, render_template
import MySQLdb, MySQLdb.cursors

app = Flask(__name__)

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

    # Connect to the database.
    db = MySQLdb.connect(host='localhost', port=3306, user='5cbookfinder', 
        passwd='g4G5IkDOM3a91EV', db='5cbookfinder', 
        cursorclass=MySQLdb.cursors.DictCursor)
    cursor = db.cursor()

    # Select the right user and raise an error if we don't have an exact match.
    # TODO: Cache these results!
    cursor.execute('SELECT * FROM Users WHERE user_id = %s', userid)
    rows_affected = cursor.rowcount
    user = cursor.fetchone()
    if int(rows_affected) is not 1:
        raise Exception

    # Get the books that we've recently listed.
    # TODO.

    # Get the books that are currently being sold that are on their wishlist.
    cursor.execute("""SELECT B.*, BFS.created_at, BFS.price, USB.user_id AS 'owner', BFSS.description AS 'condition' FROM Books B, UserTracksBook UTB, BooksForSale BFS, UserSellsBook USB, BooksForSaleStatus BFSS WHERE UTB.book_isbn = B.book_isbn AND BFS.book_isbn = B.book_isbn AND BFS.status = 1 AND BFSS.id = BFS.book_condition AND UTB.user_id = %s""", userid)
    wishlist_selling = cursor.fetchall()

    # Then, get the books that they themselves are selling.
    cursor.execute("""SELECT BFS.listing_id, BFS.book_isbn, 
        BFS.created_at, BFS.edition, BFS.price, BFS.book_condition, B.* 
        FROM BooksForSale BFS, Books B, UserSellsBook USB WHERE 
        B.book_isbn = BFS.book_isbn AND USB.listing_id = BFS.listing_id AND 
        USB.user_id = %s""", userid)
    user_selling = cursor.fetchall()

    # Get the book image from Google Books API.


    db.close()

    return render_template('user_profile.html', wishlist_selling=wishlist_selling, user_selling=user_selling, user=user)

@app.route('/book/<isbn>')
def get_book_information(isbn):
    return render_template('book.html')

@app.route('/course/<course_number>')
def get_course_information(course_number):
    return render_template('course.html')

@app.route('/search')
def get_search_json():
    return "Hello, world!"

if __name__ == '__main__':
    app.run(debug=True)

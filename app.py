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
    db = MySQLdb.connect(host='localhost', port=3306, user='5cbookfinder', passwd='g4G5IkDOM3a91EV', db='5cbookfinder', cursorclass=MySQLdb.cursors.DictCursor)
    cursor = db.cursor()

    # Select the right user and raise an error if we don't have an exact match.
    cursor.execute('SELECT user_id FROM Users WHERE user_id = %s', userid)
    rows_affected = cursor.rowcount
    if int(rows_affected) is not 1:
        raise Exception

    # Otherwise, get the books they track and sell.
    #cursor.execute('SELECT B.* FROM Books B INNER JOIN UserTracksBook UTB ON UTB.book_isbn = B.book_isbn WHERE UTB.user_id = %s', userid)
    #tracked_books = cursor.fetchall()

    cursor.execute('SELECT BFS.listing_id, BFS.book_isbn, BFS.created_at, BFS.edition, BFS.price, BFS.book_condition, B.*  FROM BooksForSale BFS, Books B, UserSellsBook USB WHERE B.book_isbn = BFS.book_isbn AND USB.listing_id = BFS.listing_id AND USB.user_id = %s', userid)
    selling_books = cursor.fetchall()

    # Books we're tracking
    #for b in tracked_books:
        
    # Books we're selling.
`

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
    return "Hello, world!"

if __name__ == '__main__':
    app.run(debug=True)

import scrape_books as sb
import MySQLdb, MySQLdb.cursors
import re
import logging
import sys, os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import config

# Global variables.
TERM = 'FA2014'

logging.basicConfig(filename='../logs/fetch_books.log', filemode='w', level=logging.INFO)

def populate_database_with_books():
    # Connect to database.
    db = MySQLdb.connect(host=config.DB_HOST, port=config.DB_PORT, \
        user=config.DB_USER, passwd=config.DB_PASSWD, db=config.DB, \
        cursorclass=MySQLdb.cursors.DictCursor)

    cursor = db.cursor()

    logging.info('Database connection successful!')

    cursor.execute('SELECT * FROM Courses')
    courses = cursor.fetchall()

    logging.info('Query for all courses successful!')

    # Dictionary to keep track of books we've already added as many courses
    # may use the same books. Keys will be isbn numbers.
    books_added = {}

    # Go through all the courses and look up the books required for that course
    # and then add them to the database if they are not already there.
    for c in courses:
        logging.info('\nGathering book information for %s' %c['course_number'])

        # Get parameters needed to fetch list of books for this course.
        school = c['campus']
        section_num = c['section']

        if int(section_num) < 10:
            section_num = '0' + str(section_num)

        term_id = c['semester_offered']
        dept = c['dept']
        course_num = re.search(dept + '(.*) ', c['course_number']).groups()[0]

        # Get list of books.
        course_params = {'school': school, 'section_num': section_num,
                'term_id': term_id, 'dept': dept, 'course_num': course_num}
        booklist = sb.extract_books_from_page(course_params)

        if type(booklist) == list:
            for b in booklist:
                # Throw a warning if the book doesn't have an ISBN.
                if b.isbn:
                    # Add book to database if not added already.
                    if b.isbn not in books_added:
                        cursor.execute('INSERT INTO Books VALUES (%s, %s, %s, %s)',
                                (b.isbn, b.author, b.title, b.edition))
                        db.commit()

                        # Record that book has been updated in database.
                        books_added[b.isbn] = True
                        logging.info('Successfully added %s to DB!' % str(b))
                    else:
                        logging.info(str(b) + ' is already in DB!')

                    # After book is in database, we want to add the respective
                    # association of the book with the course.
                    if b.required:
                        cursor.execute('INSERT INTO CourseRequiresBook VALUES (%s, %s)',
                                (c['course_number'], b.isbn))
                        db.commit()
                        logging.info('This book is required.')
                    else:
                        cursor.execute('INSERT INTO CourseRecommendsBook VALUES (%s, %s)',
                                (c['course_number'], b.isbn))
                        db.commit()
                        logging.info('This book is recommended.')
                else:
                    logging.warn('%s is invalid!' % str(b))
        else:
            logging.warn(booklist)
            logging.warn('At this url:\n' + sb.base_url % course_params)

    logging.info('Ultimate success!')
    db.close()

if __name__ == '__main__':
    populate_database_with_books()

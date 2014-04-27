from bs4 import BeautifulSoup
from collections import namedtuple
import urllib2
import re

base_url = 'http://bkstr.com/webapp/wcs/stores/servlet/booklookServlet?\
bookstore_id-1=994&term_id-1=%(term_id)s&div-1=%(school)s&\
dept-1=%(dept)s&course-1=%(course_num)s&section-1=%(section_num)s'

# Sample: This philosophy class has 3 books
phil40 = {'course_num': '040', 'term_id': 'FA2014', 'school': 'PO', 'section_num': '01', 'dept': 'PHIL'}

# Sample: This cs class should
cs105 = {'course_num': '105', 'term_id': 'FA2014', 'school': 'HM', 'section_num': '01', 'dept': 'CSCI'}

# Sample: This cs class has no books
cs70 = {'course_num': '070', 'term_id': 'SP2014', 'school': 'HM', 'section_num': '03', 'dept': 'CSCI'}

def extractBooksFromPage(course_params):
    # Open page and soupify it
    page = urllib2.urlopen(base_url % course_params)
    soup = BeautifulSoup(page.read())

    # Books generally live in this div
    book_div = soup.find('div', {'class': 'efCourseBody'})

    if book_div:
        # The list of books
        booklist = book_div.find('ul',
                {'id': 'material-group-list_REQUIRED_1_1'}).findAll('li')

        # Now to extract the data we need...
        Book = namedtuple('Book', ['title', 'edition', 'author', 'isbn'])
        clean_book_list = []

        for b in booklist:
            (title, edition) = cleanTitle(b.find('h3',
                {'class': 'material-group-title'}).text)
            author = cleanAuthor(b.find('span', {'id': 'materialAuthor'}).text)
            isbn = cleanISBN(b.find('span', {'id': 'materialISBN'}).text)
            clean_book_list.append(Book(title, edition, author, isbn))

        return clean_book_list
    else:
        return "This class has no books."

def cleanTitle(text):
    text = re.sub('\n|\t| ', ' ', str(text)).split('Edition: ')
    text = map(lambda t: t.strip(), text)

    return text

def cleanAuthor(text):
    return str(text.split('Author:')[1].strip())

def cleanISBN(text):
    return str(text.split('ISBN:')[1].strip())

print extractBooksFromPage(cs70)
print extractBooksFromPage(cs105)
print extractBooksFromPage(phil40)


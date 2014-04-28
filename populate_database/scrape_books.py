from bs4 import BeautifulSoup
from collections import namedtuple
import urllib2
import httplib
import re

# To scrape books for a certain class you need the following parameters:
#       course_num
#       term_id
#       school
#       section_num
#       dept

base_url = 'http://bkstr.com/webapp/wcs/stores/servlet/booklookServlet?\
bookstore_id-1=994&term_id-1=%(term_id)s&div-1=%(school)s&\
dept-1=%(dept)s&course-1=%(course_num)s&section-1=%(section_num)s'

# Samples
phil40 = {'course_num': '040', 'term_id': 'FA2014', 'school': 'PO', 'section_num': '01', 'dept': 'PHIL'}
cs105 = {'course_num': '105', 'term_id': 'FA2014', 'school': 'HM', 'section_num': '01', 'dept': 'CSCI'}
cs70 = {'course_num': '070', 'term_id': 'SP2014', 'school': 'HM', 'section_num': '03', 'dept': 'CSCI'}
nonexist = {'course_num': '123', 'term_id': 'SP2014', 'school': 'HM', 'section_num': '03', 'dept': 'CSCI'}

def soupify_page(url):
    page = urllib2.urlopen(url)

    try:
        contents = page.read()
    except httplib.IncompleteRead as e:
        contents = e.partial

    return BeautifulSoup(contents)

def extract_books_from_page(course_params):
    soup = soupify_page(base_url % course_params)

    # Books generally live in this div.
    book_div = soup.find('div', {'class': 'efCourseBody'})

    if book_div:
        # The list of required books.
        required_div = book_div.find('ul', {'id': 'material-group-list_REQUIRED_1_1'})
        req_booklist = required_div.findAll('li') if required_div else []

        # The list of recommended books.
        recomm_div = book_div.find('ul', {'id': 'material-group-list_RECOMMENDED_1_1'})
        rec_booklist = recomm_div.findAll('li') if recomm_div else []

        # Now to extract the data we need.
        clean_book_list = []

        clean_book_list.extend(formatBookList(req_booklist, True))
        clean_book_list.extend(formatBookList(rec_booklist, False))

        return clean_book_list
    else:
        # If the course has no books listed, we want to make sure that it
        # actually requires no books instead of us querying a non-existent
        # class.
        error_div = soup.find('div', {'id': 'efCourseErrorSection'})
        if error_div:
            msg = error_div.find('b')
            return msg.contents[0].lstrip().rstrip()
        else:
            return "Unknown error: %s" % str(error_div)

def formatBookList(blist, required):
    Book = namedtuple('Book', ['title', 'edition', 'author', 'isbn', 'required'])
    result = []

    for b in blist:
        (title, edition) = cleanTitle(b.find('h3',
            {'class': 'material-group-title'}))
        author = cleanAuthor(b.find('span', {'id': 'materialAuthor'}))
        isbn = cleanISBN(b.find('span', {'id': 'materialISBN'}))

        result.append(Book(title, edition, author, isbn, required))

    return result

def cleanTitle(tag):
    if tag:
        text = tag.text
        text = re.sub('\n|\t| ', ' ', str(text)).split('Edition: ')
        text = map(lambda t: t.strip(), text)

        return text

def cleanAuthor(tag):
    if tag:
        text = tag.text
        return str(text.split('Author:')[1].strip())

def cleanISBN(tag):
    if tag:
        text = tag.text
        return str(text.split('ISBN:')[1].strip())

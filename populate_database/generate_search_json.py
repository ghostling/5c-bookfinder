import json
import MySQLdb, MySQLdb.cursors

def main():
	# Open the necessary files.
	courses_file = open("courses.json", "w")

	books_file = open("books.json", "w")

	# Connect to the server.
	db = MySQLdb.connect(host='bookfinder.5capps.com', port=3306, user='5cbookfinder',
	     passwd='g4G5IkDOM3a91EV', db='5cbookfinder',
	     cursorclass=MySQLdb.cursors.DictCursor)
	cursor = db.cursor()

	# First, populate the courses file.
	cursor.execute('SELECT course_number, title, professor FROM Courses')
	courses_list = cursor.fetchall()

	courses_file.write(json.dumps(courses_list, indent=4, sort_keys=True))
	courses_file.close()
	print "Finish writing the courses json file as courses.json..."

	# Then, populate the books file.
	cursor.execute('SELECT book_isbn, author, title FROM Books')
	books_list = cursor.fetchall()

	books_file.write(json.dumps(books_list, indent=4, sort_keys=True))
	books_file.close()

	print "Finish writing the books json file as books.json..."

	print "Complete!"

if __name__ == "__main__":
	main()
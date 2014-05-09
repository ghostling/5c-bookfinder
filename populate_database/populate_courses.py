import requests
import urllib2
import re
from bs4 import BeautifulSoup
import json
import MySQLdb
import sys, os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import config

# NOTE: This is an adaptation of github.com/mauryquijada/5c-enrollify.

# Set up globals.
SESS = "FA"
YEAR = "2014"

BASEURL = "https://portal.claremontmckenna.edu/ics/Portlets/CRM/CXWebLinks/Por\
tlet.CXFacultyAdvisor/CXFacultyAdvisorPage.aspx?SessionID={{25715df1-32b9-42bf\
-9033-e5630cfbf34a}}&MY_SCP_NAME=/cgi-bin/course/pccrscatarea.cgi&DestURL=http\
://cx-cmc.cx.claremont.edu:51081/cgi-bin/course/pccrslistarea.cgi?crsarea=%s&\
yr={1}&sess={0}".format(SESS, YEAR)

# Given a department, it creates a list of dictionaries, each of which contains
# course information for a course in that department.
def grab_course_info_for_dept(dept_id):
	r = requests.get(BASEURL % dept_id)
	soup = BeautifulSoup(r.text)
	table = soup.find_all("table")[-1]  # last table is "All Sections"
	department_rows = table.find_all("tr", class_="glb_data_dark")

	course_list = []

	for i, t in enumerate(department_rows):
		course = create_course_dict(get_td_tags(t), dept_id)
		
		if course and course not in course_list:
			course_list.append(course)

	return course_list

# Takes a <tr> tag as input and returns all the <td> tags
# contained inside. Strips all whitespace and the `Textbook Info"
# string after the course title.
def get_td_tags(tr_tag):
	tds = [str(td.text.strip()) for td in tr_tag.find_all("td")]
	tds[-1] = remove_spaces(tds[-1])
	return tds

# Returns a string that's truncated after two double spaces (as long as it's 
# not seen in the first three characters).
def remove_spaces(string):
	if string.find("  ") < 3:
		return string[:string.find("  ", 3)]
	else:
		return string[:string.find("  ")]

# Creates a dictionary representing a course given a table row.
def create_course_dict(td_tags, dept):
	length = len(td_tags)
	course = {}

	# These are the only row lengths that show full sections.
	if length == 12 or length == 14:
		course["number"] = remove_spaces(td_tags[0]).replace(" ", "")
		course["dept"] = dept
		course["section"] = td_tags[1]
		course["instructor"] = td_tags[2]
		course["campus"] = td_tags[7]
		course["bldg"] = td_tags[8]

		if length == 12:
			course["title"] = td_tags[11]
			return course

		else:
			course["title"] = td_tags[13]
			return course

	elif length in [6, 7, 8]:
		return False
	else:
		print "Oops! %d inner <td> tags at index %d" % (length, index)
		return False

def populate_courses_json():
	# Declare globals.
	global SESS
	global YEAR

	# Open the file containing all of the departments.
	f = open("depts.json", "r")
	depts = json.loads(f.read())
	f.close()

	# Open a new depts_courses.json file.
	f = open("courses_{0}{1}.json".format(SESS, YEAR), "w")
	course_list = []

	# Fetch all course information and dump it into that file.
	for dept in depts:
		print "Grabbing course information for {0}...".format(dept)
		course_info = grab_course_info_for_dept(dept)
		course_list += course_info

	f.write(json.dumps(course_list, indent=4, sort_keys=True))
	f.close()

	return course_list

def populate_database_with_courses():
    semester_offered = SESS + YEAR

    # Assume we have the JSON file in the same directory and use it.
    f = open("courses_{0}{1}.json".format(SESS, YEAR), "r")
    courses = json.loads(f.read())
    f.close()

    # Prepare the connection to the database.
    db = MySQLdb.connect(host=config.DB_HOST, port=config.DB_PORT, \
    	user=config.DB_USER, passwd=config.DB_PASSWD, db=config.DB)
    cursor = db.cursor()

    courses_added = {}

    # Add each of the courses individally to the database.
    for course in courses:
        # Create the course number attribute.
        course["number"] = course["number"] + " " + course["campus"] \
        + "-" + course["section"]

        # Add default value to campus if it isn't available.
        if not course["campus"]:
            course["campus"] = "NA"

        # Add default value to building if it isn't available.
        if not course["bldg"]:
        	course["bldg"] = "NA"
        
        # Only insert if we haven't seen it before (put in place for
        # crosslisted courses).
        if course["number"] not in courses_added:
            # Grab the department from the course code. This is seen as the
            # "ultimate" department, preferred in case the course is cross-listed.
            dept = re.match("^([A-Z]+).*", course["number"]).group(1)
            # Insert it!
            cursor.execute('''INSERT INTO Courses VALUES
            	(%s, %s, %s, %s, %s, %s, %s, %s)''',
            	(course["number"], course["section"], dept, \
            		course["instructor"], course["title"], \
            		semester_offered, course["campus"], course["bldg"]))
            db.commit()

        # Add the course to the hash table.
        courses_added[course["number"]] = True
    
    db.close()

if __name__ == "__main__":
	populate_database_with_courses()

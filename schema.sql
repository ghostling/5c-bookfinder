CREATE TABLE CurrentSemester(
    semester VARCHAR(8) PRIMARY KEY,
    is_current_semester TINYINT(1) NOT NULL
);

CREATE TABLE Courses (
    course_number VARCHAR(32) PRIMARY KEY,
    section TINYINT(2) NOT NULL,
    dept CHAR(4) NOT NULL,
    professor VARCHAR(64),
    title VARCHAR(256) NOT NULL,
    semester_offered VARCHAR(8) NOT NULL,
    campus CHAR(4) NOT NULL,
    building CHAR(4),
    FOREIGN KEY (semester_offered) REFERENCES CurrentSemester(semester)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

CREATE TABLE Books (
    isbn VARCHAR(16) PRIMARY KEY,
    author VARCHAR(256) NOT NULL,
    title VARCHAR(256) NOT NULL,
    edition VARCHAR(8)
);

CREATE TABLE RecentlyUsed (
    last_active DATETIME PRIMARY KEY,
    recently_used TINYINT(1)
);

CREATE TABLE Users (
    uid INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    email VARCHAR(256) UNIQUE NOT NULL,
    hashed_pw VARCHAR(128) NOT NULL,
    phone VARCHAR(16),
    last_active DATETIME DEFAULT NULL,
    FOREIGN KEY (last_active) REFERENCES RecentlyUsed(last_active)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
);

CREATE TABLE Admins(
    uid INTEGER PRIMARY KEY,
    FOREIGN KEY (uid) REFERENCES Users(uid)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE BookCondition(
    rating TINYINT(2) PRIMARY KEY,
    description VARCHAR(32)
);

CREATE TABLE BooksForSale (
    listing_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(16) NOT NULL,
    seller_id INTEGER NOT NULL,
    status TINYINT(1) NOT NULL, # 0 -- Inactive, 1 -- Active; for sale, 2 -- Sold.
    created_at DATETIME DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    comments VARCHAR(256),
    price DOUBLE(5, 2) NOT NULL,
    rating TINYINT(2) NOT NULL,
    FOREIGN KEY (isbn) REFERENCES Books(isbn)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES Users(uid)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (rating) REFERENCES BookCondition(rating)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

CREATE TABLE UserTracksBook (
    uid INTEGER NOT NULL,
    isbn VARCHAR(16) NOT NULL,
    PRIMARY KEY (uid, isbn),
    FOREIGN KEY (uid) REFERENCES Users(uid)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (isbn) REFERENCES Books(isbn)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE CourseRequiresBook (
    course_number VARCHAR(32),
    isbn VARCHAR(16),
    FOREIGN KEY (course_number) REFERENCES Courses(course_number)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (isbn) REFERENCES Books(isbn)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    PRIMARY KEY (course_number, isbn)
);

CREATE TABLE CourseRecommendsBook (
    course_number VARCHAR(32),
    isbn VARCHAR(16),
    FOREIGN KEY (course_number) REFERENCES Courses(course_number)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (isbn) REFERENCES Books(isbn)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    PRIMARY KEY (course_number, isbn)
);

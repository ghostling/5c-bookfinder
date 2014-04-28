CREATE TABLE Courses (
    course_number VARCHAR(32) PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    professor VARCHAR(64),
    semester_offered VARCHAR(8) NOT NULL,
    dept CHAR(4) NOT NULL,
    campus CHAR(4) NOT NULL,
    section TINYINT(2) NOT NULL
);

CREATE TABLE Books (
    author VARCHAR(256) NOT NULL,
    book_isbn VARCHAR(16) PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    edition VARCHAR(8)
);

CREATE TABLE BooksForSaleStatus (
    id TINYINT PRIMARY KEY,
    state VARCHAR(64) NOT NULL
);

CREATE TABLE BooksForSale (
    listing_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    book_isbn VARCHAR(16) NOT NULL,
    status TINYINT(1) NOT NULL , # 0 -- Inactive record, 1 -- Active record, for sale, 2 -- Sold.
    created_at DATETIME DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    edition VARCHAR(16),
    price DOUBLE(4, 2) NOT NULL,
    book_condition TINYINT(1) NOT NULL,
    FOREIGN KEY (book_isbn) REFERENCES Books(book_isbn)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (book_condition) REFERENCES BooksForSaleStatus(id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

CREATE TABLE Users (
    user_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64),
    email_address VARCHAR(256),
    hashed_password VARCHAR(2048),
    phone_number VARCHAR(16)
);

CREATE TABLE UserSellsBook (
    user_id INTEGER NOT NULL,
    listing_id INTEGER NOT NULL,
    FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (listing_id)
        REFERENCES BooksForSale(listing_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    PRIMARY KEY (user_id, listing_id)
);

CREATE TABLE UserTracksBook (
    user_id INTEGER NOT NULL,
    book_isbn VARCHAR(16) NOT NULL,
    PRIMARY KEY (user_id, book_isbn),
    FOREIGN KEY (user_id)
        REFERENCES Users (user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (book_isbn)
        REFERENCES Books (book_isbn)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE CourseRequiresBook (
    course_number VARCHAR(32),
    book_isbn VARCHAR(16),
    FOREIGN KEY (course_number)
        REFERENCES Courses(course_number)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (book_isbn)
        REFERENCES Books(book_isbn)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    PRIMARY KEY (course_number, book_isbn)
);

CREATE TABLE CourseRecommendsBook (
    course_number VARCHAR(32),
    book_isbn VARCHAR(16),
    FOREIGN KEY (course_number)
        REFERENCES Courses(course_number)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (book_isbn)
        REFERENCES Books(book_isbn)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    PRIMARY KEY (course_number, book_isbn)
);

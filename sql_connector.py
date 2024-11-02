import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


db = mysql.connector.connect(
    host = os.getenv("DB_HOST"),
    user = os.getenv("DB_USER"),
    passwd = os.getenv("DB_PASS"),
    database = os.getenv("DB_NAME")
)

cursor = db.cursor()

cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

table_names = ['alumni', 'course_taken', 'thesis', 'forms', 'graduation_application'
               'forms_classes', 'program', 'MS_requirements', 'MS_required_courses',
               'PhD_requirements', 'PhD_required_courses', 'application', 'transcript', 
               'recommendationletter', 'reviewform', 'priordegrees', 'been_reviewed', 
               'pre_app', 'schedule', 'enrollment', 'user', 'student', 'course', 
               'prerequisite']

for name in table_names:
    query = """DROP TABLE IF EXISTS """ + name + ";"
    cursor.execute(query)

query = """DROP TABLE IF EXISTS forms_classes;"""
cursor.execute(query)
query = """DROP TABLE IF EXISTS graduation_application;"""
cursor.execute(query)

#ALL TABLES HERE ARE FROM ADS AND UNCHANGED#
query = """
    CREATE TABLE IF NOT EXISTS alumni (
    university_id       VARCHAR(50) NOT NULL,
    user_id             INTEGER NOT NULL,
    year_of_graduation  INT(4) NOT NULL,
    program     VARCHAR(4) NOT NULL,
    major       VARCHAR(50),
    gpa                 VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS course_taken (
    university_id       VARCHAR(50) NOT NULL,
    dept                VARCHAR(4) NOT NULL,
    course_num          INT NOT NULL,
    course_title        VARCHAR(50) NOT NULL,
    credits             INT NOT NULL,
    semester_taken      VARCHAR(20) NOT NULL,
    year                int NOT NULL,
    grade               VARCHAR(10) DEFAULT 'IP',
    crn                 VARCHAR(50)
);
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS thesis (
    form_id                            INTEGER PRIMARY KEY AUTO_INCREMENT,
    thesis                             TEXT,
    submitted_university_id            VARCHAR(50) NOT NULL,
    FOREIGN KEY (submitted_university_id) REFERENCES student (uid),  
    FOREIGN KEY (form_id) REFERENCES forms (form_id)
);
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS forms (
    form_id                            INTEGER PRIMARY KEY AUTO_INCREMENT,
    submitted_university_id            VARCHAR(50) NOT NULL,
    approved                           BIT DEFAULT 0,
    FOREIGN KEY (submitted_university_id) REFERENCES student (uid)
);
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS graduation_application (
    form_id                            INTEGER PRIMARY KEY AUTO_INCREMENT,
    submitted_university_id            VARCHAR(50) NOT NULL,
    approved                           BIT DEFAULT 0,
    FOREIGN KEY (submitted_university_id) REFERENCES student (uid)
);
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS forms_classes (
    form_id             INTEGER,
    university_id       VARCHAR(50) NOT NULL,
    dept                VARCHAR(4) NOT NULL,
    course_num          INT NOT NULL,
    credits             INT NOT NULL,
    FOREIGN KEY (dept, course_num) REFERENCES course (department, course_num)
);
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS program (
    program_id INT NOT NULL,
    program_field VARCHAR(50) NOT NULL,
    program_degree VARCHAR(4) NOT NULL,
    program_gpa_min FLOAT NOT NULL,
    credit_hrs INT NOT NULL,
    credit_hrs_prgm INT NOT NULL,
    courses_non_prgm INT NOT NULL,
    below_b INT NOT NULL,
    thesis BIT NOT NULL
);
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS MS_requirements(
    min_gpa                         VARCHAR(50),
    min_credit_hours                INTEGER,
    most_courses_outside_CS         INTEGER,
    most_grades_below_B               INTEGER
);
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS MS_required_courses(
    dept                VARCHAR(4) NOT NULL,
    course_num          INT NOT NULL,
    course_title        VARCHAR(50) NOT NULL,
    credits             INT NOT NULL
);
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS PhD_requirements(
    min_gpa                         VARCHAR(50),
    min_credit_hours                INTEGER,
    min_credits_in_cs               INTEGER,
    most_grades_below_B             INTEGER,
    pass_thesis_Defense             BIT NOT NULL DEFAULT 0
);
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS PhD_required_courses(
    dept                VARCHAR(4) NOT NULL,
    course_num          INT NOT NULL,
    course_title        VARCHAR(50) NOT NULL,
    credits             INT NOT NULL
);
"""
cursor.execute(query)

#END OF TABLES FROM ADS THAT ARE UNCHANGED#

#ALL TABLES HERE ARE FROM APPS AND UNCHANGED#
query = """
CREATE TABLE application (
    `applicationid` int NOT NULL AUTO_INCREMENT, 
    `user_id` int UNIQUE, 
    `status` enum(
        'application incomplete', 'application complete and under review', 'decision'
    ) DEFAULT NULL, `decision` enum(
        'admit', 'admit with aid', 'reject', 'undecided'
    ) DEFAULT NULL, `timestamp` date NOT NULL, `firstname` varchar(50) DEFAULT NULL, 
    `lastname` varchar(50) DEFAULT NULL, `address` varchar(255) DEFAULT NULL, 
    `ssn` varchar(255) UNIQUE, `phonenumber` varchar(255) DEFAULT NULL, 
    `degreessought` enum('MS', 'PHD') DEFAULT NULL, 
    `areas_interest` varchar(255) DEFAULT NULL, `priordegrees` enum('BS', 'MS') DEFAULT NULL, 
    `greverbal` varchar(3) DEFAULT NULL, `grequantitative` varchar(3) DEFAULT NULL, `greyearofexam` varchar(4) DEFAULT NULL, `greadvancedscore` varchar(3) DEFAULT NULL, `greadvancedsubject` varchar(255) DEFAULT NULL, `priorwork` varchar(255) DEFAULT NULL, `uid` varchar(255) UNIQUE, `semester` varchar(10) DEFAULT NULL, `year` varchar(4) DEFAULT NULL, 
    `transcript_submission`   enum('online', 'email', 'mail') DEFAULT NULL,
    `transcript_submission_received`  enum('received', 'not received') DEFAULT 'not received',
    `transcript_filename`     varchar(100) DEFAULT NULL,
    PRIMARY KEY (`applicationid`, `user_id`, `ssn`, `uid`)) ENGINE = InnoDB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
"""
cursor.execute(query)

query = """
CREATE TABLE transcript (
    transcriptid INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    transcriptstatus VARCHAR(255) CHECK(transcriptstatus IN ('received', 'not received')) DEFAULT 'not received',
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS recommendationletter (
    `letterid` int NOT NULL AUTO_INCREMENT, 
    `user_id` int DEFAULT NULL, 
    `rec_name_one` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL, 
    `rec_email_one` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL, 
    `rec_letter_one` varchar(255) DEFAULT NULL, 
    `status_one` enum('received', 'not received') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'not received', 
    `rec_name_two` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL, 
    `rec_email_two` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL, 
    `rec_letter_two` varchar(255) DEFAULT NULL, 
    `status_two` enum('received', 'not received') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'not received', 
    `rec_name_three` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL, 
    `rec_email_three` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL, 
    `rec_letter_three` varchar(255) DEFAULT NULL, 
    `status_three` enum('received', 'not received') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'not received', 
    code varchar(100) DEFAULT NULL,
    all_received enum('received', 'not received') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'not received', 
    PRIMARY KEY (`letterid`), KEY `user_id` (`user_id`), CONSTRAINT `recommendationletter_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE = InnoDB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
"""
cursor.execute(query)

query = """
CREATE TABLE reviewform (
    `reviewid` int NOT NULL AUTO_INCREMENT, 
    `user_id` int DEFAULT NULL, 
    `reviewerid` int NOT NULL, 
    `rating` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL, 
    `generic` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL, 
    `credible` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL, 
    `gas_decision` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL, 
    `missing_course` varchar(255) DEFAULT NULL, 
    `reasons_reject` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL, 
    `reviewer_comment` varchar(255) DEFAULT NULL, 
    `recommended_advisor` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL, 
    `review_status` varchar(255) DEFAULT NULL, 
    `finaldecision` enum(
        'reject', 'admit', 'admit with aid', 'undecided'
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'undecided', `timestamp` date DEFAULT NULL, PRIMARY KEY (`reviewid`, `reviewerid`), UNIQUE KEY `unique_reviewerid_user_id` (`reviewerid`, `user_id`), KEY `user_id_index` (`user_id`)
) ENGINE = InnoDB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS priordegrees (
    `applicationid` int DEFAULT NULL, `user_id` int NOT NULL, `degree_type` enum('BS', 'MS') NOT NULL, `year` varchar(4) DEFAULT NULL, `gpa` varchar(4) DEFAULT NULL, `school` varchar(255) DEFAULT NULL, `major` varchar(100) DEFAULT NULL COMMENT 'New column', PRIMARY KEY (`user_id`, `degree_type`), KEY `applicationid` (`applicationid`), CONSTRAINT `priordegrees_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`), CONSTRAINT `priordegrees_ibfk_2` FOREIGN KEY (`applicationid`) REFERENCES `application` (`applicationid`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS been_reviewed (
    `reviewerid` int NOT NULL, `reviewid` int NOT NULL, PRIMARY KEY (`reviewerid`, `reviewid`), KEY `FK_reviewid` (`reviewid`), CONSTRAINT `FK_reviewerid` FOREIGN KEY (`reviewerid`) REFERENCES `user` (`user_id`), CONSTRAINT `FK_reviewid` FOREIGN KEY (`reviewid`) REFERENCES `application` (`applicationid`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS pre_app (
    `user_id` int NOT NULL AUTO_INCREMENT, `email` varchar(50) NOT NULL, `username` varchar(50) NOT NULL, `password` varchar(50) NOT NULL, `role` enum(
        'applicant', 'admin', 'reviewer', 'user', 'gs', 'cac'
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'user', PRIMARY KEY (`user_id`, `email`)
) ENGINE = InnoDB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
"""
cursor.execute(query)

#END OF TABLES FROM APPS THAT ARE UNCHANGED#

#ALL TABLES HERE ARE FROM REGS AND UNCHANGED#


query = """
CREATE TABLE IF NOT EXISTS schedule (
  course_dept   varchar(50) not null,
  course_num    int(4) not null,
  schedule_day  varchar(10) CHECK( schedule_day IN ('M', 'T', 'W', 'R', 'F') ) not null,
  start_time    time CHECK( start_time IN ('15:00', '16:00', '18:00') ) not null,
  end_time      time CHECK( end_time IN ('17:30', '18:30', '20:30') ) not null,
  instructor_id INTEGER,
  room          varchar(50),
  room_capacity int(4),
  semester      varchar(10) CHECK( semester IN ('Fall', 'Spring', 'Summer' ) ) not null,
  year          int(4) not null,
  crn           VARCHAR(50) GENERATED ALWAYS AS (
    CONCAT(
        CAST(ASCII(SUBSTRING(course_dept, 1, 1)) - ASCII('A') + 1 AS CHAR),
        CAST(ASCII(SUBSTRING(course_dept, 2, 1)) - ASCII('A') + 1 AS CHAR),
        CAST(ASCII(SUBSTRING(course_dept, 3, 1)) - ASCII('A') + 1 AS CHAR),
        CAST(ASCII(SUBSTRING(course_dept, 4, 1)) - ASCII('A') + 1 AS CHAR),
        course_num,
        CASE semester
            WHEN 'Fall' THEN '1'
            WHEN 'Spring' THEN '2'
            WHEN 'Summer' THEN '3'
        END,
        year - 2021
    )
  ) STORED,
  primary key (course_dept, course_num, semester, year),
  foreign key (course_dept, course_num) references course(department, course_num),
  foreign key (instructor_id) references user(user_id)
);
"""
cursor.execute(query)

query = """CREATE INDEX idx_crn ON schedule(crn)"""
cursor.execute(query)

query = """
CREATE TABLE IF NOT EXISTS enrollment (
  student_uid  VARCHAR(50) not null,
  crn          VARCHAR(50) not null,
  grade        varchar(2) DEFAULT 'IP' CHECK(grade IN ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP')),
  primary key (student_uid, crn),
  foreign key (student_uid) references student(uid),
  foreign key (crn) references schedule(crn)
);
"""
cursor.execute(query)

#END OF TABLES FROM REGS THAT ARE UNCHANGED#

#THE FOLLOWING TABLES HAVE BEEN MODIFIED FROM ADS, REGS, APPS#
#from_what_database: original_table_name#


#ADS: user#
#REGS: user#
#APPS: user#
query = """
CREATE TABLE IF NOT EXISTS user(
    user_id             INTEGER PRIMARY KEY AUTO_INCREMENT,
    email               varchar(50)  NOT NULL UNIQUE,
    username            varchar(50) NOT NULL,
    password            varchar(50) NOT NULL,
    first_name          VARCHAR(50),
    last_name           VARCHAR(50),
    dob                 date,
    address             VARCHAR(50),
    role                VARCHAR(50) CHECK(role IN ('admin', 'grad_sec', 'cac', 'fac_adv', 'reviewer', 'instructor', 'grad_stu', 'alumni', 'applicant', 'user', 'registrar')) DEFAULT 'user'
);
"""
cursor.execute(query)

#ADS: student#
#REGS: student#
query = """
CREATE TABLE IF NOT EXISTS student(
    uid                 VARCHAR(50) UNIQUE,
    user_id             INTEGER UNIQUE,
    advisor_id          INTEGER,
    program             VARCHAR(50) CHECK(program IN ('MS', 'PhD')),
    major               VARCHAR(50),
    gpa                 VARCHAR(50),
    cleared             BIT DEFAULT 0,
    advising_hold       BIT DEFAULT 0
);
"""
cursor.execute(query)

#ADS: course#
#REGS: course#
query = """
CREATE TABLE IF NOT EXISTS course (
    department          VARCHAR(4) NOT NULL,
    course_num          INT NOT NULL,
    title               VARCHAR(50) NOT NULL,
    credit              INT NOT NULL,
    primary key (department, course_num)
);
"""
cursor.execute(query)

#ADS: prerequisite#
#REGS: prerequisite#
query = """
CREATE TABLE IF NOT EXISTS prerequisite (
    course_dep          VARCHAR(4),
    course_num          INT,
    prereq_one_dep          VARCHAR(4),
    prereq_one_num          INT NOT NULL,
    prereq_two_dep          VARCHAR(4),
    prereq_two_num          INT NOT NULL,
    foreign key (course_dep, course_num) references course(department, course_num),
    foreign key (prereq_one_dep, prereq_one_num) references course(department, course_num),
    foreign key (prereq_two_dep, prereq_two_num) references course(department, course_num)
);
"""
cursor.execute(query)

#END OF TABLES FROM DATABASE THAT HAVE BEEN MODIFIED#

#THE FOLLOWING INSERTIONS ARE TEST USER ACCOUNTS FOR EACH ROLE#

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(1, 'admin@gwu.edu', 'adminuser', 'adminpass', 'fadmin', 'ladmin', '2000-01-01', '123 Admin St., City, State 00000', 'admin')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(2, 'gradsec@gwu.edu', 'secretaryuser', 'secretarypass', 'fsecretary', 'lsecretary', '2000-01-01', '123 Admin St., City, State 00000', 'grad_sec')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(3, 'facadv@gwu.edu', 'advisoruser', 'advisorpass', 'fadvisor', 'ladvisor', '2000-01-01', '123 Admin St., City, State 00000', 'fac_adv')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(4, 'reviewer@gwu.edu', 'revieweruser', 'reviewerpass', 'freviewer', 'lreviewer', '2000-01-01', '123 Admin St., City, State 00000', 'reviewer')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(5, 'instructor@gwu.edu', 'instructoruser', 'instructorpass', 'finstructor', 'linstructor', '2000-01-01', '123 Admin St., City, State 00000', 'instructor')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(6, 'MSgradstu@gwu.edu', 'MSgradstuuser', 'MSgradstupass', 'fMSgradstu', 'lMSgradstu', '2000-01-01', '123 Admin St., City, State 00000', 'grad_stu')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(7, 'PhDgradstu@gwu.edu', 'PhDgradstuuser', 'PhDgradstupass', 'fPhDgradstu', 'lPhDgradstu', '2000-01-01', '123 Admin St., City, State 00000', 'grad_stu')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(8, 'alumni@gwu.edu', 'alumniuser', 'alumnipass', 'falumni', 'lalumni', '2000-01-01', '123 Admin St., City, State 00000', 'alumni')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(9, 'applicant@gwu.edu', 'applicantuser', 'applicantpass', 'fapplicant', 'lapplicant', '2000-01-01', '123 Admin St., City, State 00000', 'applicant')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(10, 'user@gwu.edu', 'useruser', 'userpass', 'fuser', 'luser', '2000-01-01', '123 Admin St., City, State 00000', 'user')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(11, 'cac@gwu.edu', 'cacuser', 'cacpass', 'fcac', 'lcac', '2000-01-01', '123 Admin St., City, State 00000', 'cac')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(12, 'i1@gwu.edu', 'i1user', 'pass', 'Peter', 'Jenkins', '2000-01-01', '123 Admin St., City, State 00000', 'instructor')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(13, 'i2@gwu.edu', 'i2user', 'pass', 'Mohnish', 'Muppagouni', '2000-01-01', '123 Admin St., City, State 00000', 'instructor')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(14, 'i3@gwu.edu', 'i3user', 'pass', 'Joseph', 'Song', '2000-01-01', '123 Admin St., City, State 00000', 'instructor')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(15, 'adv@gwu.edu', 'advuser', 'pass', 'Michael', 'Kim', '2000-01-01', '123 Admin St., City, State 00000', 'fac_adv')
"""
cursor.execute(query)

query = """
INSERT INTO user 
(user_id, email, username, password, first_name, last_name, dob, address, role)
VALUES
(16, 'reg@gwu.edu', 'reguser', 'pass', 'Daniel', 'White', '2000-01-01', '123 Admin St., City, State 00000', 'registrar')
"""
cursor.execute(query)

#END OF TEST ACCOUNTS FOR EACH ROLE#

#THE FOLLOWING INSERTIONS ARE TEST STUDENTS#

query = """
INSERT INTO student 
(uid, user_id, advisor_id, program, major, gpa, cleared)
VALUES
('00000000', 6, 3, 'MS', 'Computer Science', '0.0', 0)
"""
cursor.execute(query)

query = """
INSERT INTO student 
(uid, user_id, advisor_id, program, major, gpa, cleared)
VALUES
('00000001', 7, 3, 'PhD', 'Computer Science', '0.0', 0)
"""
cursor.execute(query)

#END OF TEST STUDENTS#

#INSERTING COURSES AND PREREQUISITES#
query = """
INSERT INTO course (department, course_num, title, credit) VALUES 
('CSCI', 6221, 'SW Paradigms', 3),
('CSCI', 6461, 'Computer Architecture', 3),
('CSCI', 6212, 'Algorithms', 3),
('CSCI', 6220, 'Machine Learning', 3),
('CSCI', 6232, 'Networks 1', 3),
('CSCI', 6233, 'Networks 2', 3),
('CSCI', 6241, 'Database 1', 3),
('CSCI', 6242, 'Database 2', 3),
('CSCI', 6246, 'Compilers', 3),
('CSCI', 6260, 'Multimedia', 3),
('CSCI', 6251, 'Cloud Computing', 3),
('CSCI', 6254, 'SW Engineering', 3),
('CSCI', 6262, 'Graphics 1', 3),
('CSCI', 6283, 'Security 1', 3),
('CSCI', 6284, 'Cryptography', 3),
('CSCI', 6286, 'Network Security', 3),
('CSCI', 6325, 'Algorithms 2', 3),
('CSCI', 6339, 'Embedded Systems', 3),
('CSCI', 6384, 'Cryptography 2', 3),
('ECE', 6241, 'Communication Theory', 3),
('ECE', 6242, 'Information Theory', 2),
('MATH', 6210, 'Logic', 2);
"""
cursor.execute(query)

query = """
INSERT INTO prerequisite (course_dep, course_num, prereq_one_dep, prereq_one_num, prereq_two_dep, prereq_two_num) VALUES
('CSCI', 6221, 'NULL', 'NULL', 'NULL', 'NULL'),
('CSCI', 6461, 'NULL', 'NULL', 'NULL', 'NULL'),
('CSCI', 6212, 'NULL', 'NULL', 'NULL', 'NULL'),
('CSCI', 6220, 'NULL', 'NULL', 'NULL', 'NULL'),
('CSCI', 6232, 'NULL', 'NULL', 'NULL', 'NULL'),
('CSCI', 6233, 'CSCI', 6232, 'NULL', 'NULL'),
('CSCI', 6241, 'NULL', 'NULL', 'NULL', 'NULL'),
('CSCI', 6242, 'CSCI', 6241, 'NULL', 'NULL'),
('CSCI', 6246, 'CSCI', 6461, 'CSCI', 6212),
('CSCI', 6260, 'NULL', 'NULL', 'NULL', 'NULL'),
('CSCI', 6251, 'CSCI', 6461, 'NULL', 'NULL'),
('CSCI', 6254, 'CSCI', 6221, 'NULL', 'NULL'),
('CSCI', 6262, 'NULL', 'NULL', 'NULL', 'NULL'),
('CSCI', 6283, 'CSCI', 6212, 'NULL', 'NULL'),
('CSCI', 6284, 'CSCI', 6212, 'NULL', 'NULL'),
('CSCI', 6286, 'CSCI', 6283, 'CSCI', 6232),
('CSCI', 6325, 'CSCI', 6212, 'NULL', 'NULL'),
('CSCI', 6339, 'CSCI', 6461, 'CSCI', 6212),
('CSCI', 6384, 'CSCI', 6284, 'NULL', 'NULL'),
('ECE', 6241, 'NULL', 'NULL', 'NULL', 'NULL'),
('ECE', 6242, 'NULL', 'NULL', 'NULL', 'NULL'),
('MATH', 6210, 'NULL', 'NULL', 'NULL', 'NULL');
"""
cursor.execute(query)

query = """
INSERT INTO schedule (course_dept, course_num, schedule_day, start_time, end_time, instructor_id, room, room_capacity, semester, year) VALUES
('CSCI', 6221, 'M', '15:00', '17:30', 12, null, null, 'Spring', 2022),
('CSCI', 6461, 'T', '15:00', '17:30', 5, null, null, 'Spring', 2022),
('CSCI', 6212, 'W', '15:00', '17:30', 5, null, null, 'Spring', 2022),
('CSCI', 6232, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('CSCI', 6233, 'T', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('CSCI', 6241, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('CSCI', 6242, 'R', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('CSCI', 6246, 'T', '15:00', '17:30', 12, null, null, 'Spring', 2022),
('CSCI', 6251, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('CSCI', 6254, 'M', '15:00', '17:30', 12, null, null, 'Spring', 2022),
('CSCI', 6260, 'R', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('CSCI', 6262, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('CSCI', 6283, 'T', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('CSCI', 6284, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('CSCI', 6286, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('CSCI', 6384, 'W', '15:00', '17:30', 12, null, null, 'Spring', 2022),
('ECE', 6241, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('ECE', 6242, 'T', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('MATH', 6210, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2022),
('CSCI', 6339, 'R', '16:00', '18:30', 12, null, null, 'Spring', 2022),

('CSCI', 6221, 'M', '15:00', '17:30', 13, null, null, 'Summer', 2022),
('CSCI', 6461, 'T', '15:00', '17:30', 5, null, null, 'Summer', 2022),
('CSCI', 6212, 'W', '15:00', '17:30', 5, null, null, 'Summer', 2022),
('CSCI', 6232, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('CSCI', 6233, 'T', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('CSCI', 6241, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('CSCI', 6242, 'R', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('CSCI', 6246, 'T', '15:00', '17:30', 13, null, null, 'Summer', 2022),
('CSCI', 6251, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('CSCI', 6254, 'M', '15:00', '17:30', 13, null, null, 'Summer', 2022),
('CSCI', 6260, 'R', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('CSCI', 6262, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('CSCI', 6283, 'T', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('CSCI', 6284, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('CSCI', 6286, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('CSCI', 6384, 'W', '15:00', '17:30', 13, null, null, 'Summer', 2022),
('ECE', 6241, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('ECE', 6242, 'T', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('MATH', 6210, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2022),
('CSCI', 6339, 'R', '16:00', '18:30', 13, null, null, 'Summer', 2022),

('CSCI', 6221, 'M', '15:00', '17:30', 14, null, null, 'Fall', 2022),
('CSCI', 6461, 'T', '15:00', '17:30', 5, null, null, 'Fall', 2022),
('CSCI', 6212, 'W', '15:00', '17:30', 5, null, null, 'Fall', 2022),
('CSCI', 6232, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('CSCI', 6233, 'T', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('CSCI', 6241, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('CSCI', 6242, 'R', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('CSCI', 6246, 'T', '15:00', '17:30', 14, null, null, 'Fall', 2022),
('CSCI', 6251, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('CSCI', 6254, 'M', '15:00', '17:30', 14, null, null, 'Fall', 2022),
('CSCI', 6260, 'R', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('CSCI', 6262, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('CSCI', 6283, 'T', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('CSCI', 6284, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('CSCI', 6286, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('CSCI', 6384, 'W', '15:00', '17:30', 14, null, null, 'Fall', 2022),
('ECE', 6241, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('ECE', 6242, 'T', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('MATH', 6210, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2022),
('CSCI', 6339, 'R', '16:00', '18:30', 14, null, null, 'Fall', 2022),

('CSCI', 6221, 'M', '15:00', '17:30', 12, null, null, 'Spring', 2023),
('CSCI', 6461, 'T', '15:00', '17:30', 5, null, null, 'Spring', 2023),
('CSCI', 6212, 'W', '15:00', '17:30', 5, null, null, 'Spring', 2023),
('CSCI', 6232, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6233, 'T', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6241, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6242, 'R', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6246, 'T', '15:00', '17:30', 12, null, null, 'Spring', 2023),
('CSCI', 6251, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6254, 'M', '15:00', '17:30', 12, null, null, 'Spring', 2023),
('CSCI', 6260, 'R', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6262, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6283, 'T', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6284, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6286, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6384, 'W', '15:00', '17:30', 12, null, null, 'Spring', 2023),
('ECE', 6241, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('ECE', 6242, 'T', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('MATH', 6210, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6339, 'R', '16:00', '18:30', 12, null, null, 'Spring', 2023),

('CSCI', 6221, 'M', '15:00', '17:30', 13, null, null, 'Summer', 2023),
('CSCI', 6461, 'T', '15:00', '17:30', 5, null, null, 'Summer', 2023),
('CSCI', 6212, 'W', '15:00', '17:30', 5, null, null, 'Summer', 2023),
('CSCI', 6232, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('CSCI', 6233, 'T', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('CSCI', 6241, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('CSCI', 6242, 'R', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('CSCI', 6246, 'T', '15:00', '17:30', 13, null, null, 'Summer', 2023),
('CSCI', 6251, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('CSCI', 6254, 'M', '15:00', '17:30', 13, null, null, 'Summer', 2023),
('CSCI', 6260, 'R', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('CSCI', 6262, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('CSCI', 6283, 'T', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('CSCI', 6284, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('CSCI', 6286, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('CSCI', 6384, 'W', '15:00', '17:30', 13, null, null, 'Summer', 2023),
('ECE', 6241, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('ECE', 6242, 'T', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('MATH', 6210, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2023),
('CSCI', 6339, 'R', '16:00', '18:30', 13, null, null, 'Summer', 2023),

('CSCI', 6221, 'M', '15:00', '17:30', 14, null, null, 'Fall', 2023),
('CSCI', 6461, 'T', '15:00', '17:30', 5, null, null, 'Fall', 2023),
('CSCI', 6212, 'W', '15:00', '17:30', 5, null, null, 'Fall', 2023),
('CSCI', 6232, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('CSCI', 6233, 'T', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('CSCI', 6241, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('CSCI', 6242, 'R', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('CSCI', 6246, 'T', '15:00', '17:30', 14, null, null, 'Fall', 2023),
('CSCI', 6251, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('CSCI', 6254, 'M', '15:00', '17:30', 14, null, null, 'Fall', 2023),
('CSCI', 6260, 'R', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('CSCI', 6262, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('CSCI', 6283, 'T', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('CSCI', 6284, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('CSCI', 6286, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('CSCI', 6384, 'W', '15:00', '17:30', 14, null, null, 'Fall', 2023),
('ECE', 6241, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('ECE', 6242, 'T', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('MATH', 6210, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2023),
('CSCI', 6339, 'R', '16:00', '18:30', 14, null, null, 'Fall', 2023),

('CSCI', 6221, 'M', '15:00', '17:30', 12, null, null, 'Spring', 2024),
('CSCI', 6461, 'T', '15:00', '17:30', 5, null, null, 'Spring', 2024),
('CSCI', 6212, 'W', '15:00', '17:30', 5, null, null, 'Spring', 2024),
('CSCI', 6232, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6233, 'T', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6241, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6242, 'R', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6246, 'T', '15:00', '17:30', 12, null, null, 'Spring', 2024),
('CSCI', 6251, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6254, 'M', '15:00', '17:30', 12, null, null, 'Spring', 2024),
('CSCI', 6260, 'R', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6262, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6283, 'T', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6284, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6286, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6384, 'W', '15:00', '17:30', 12, null, null, 'Spring', 2024),
('ECE', 6241, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('ECE', 6242, 'T', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('MATH', 6210, 'W', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6339, 'R', '16:00', '18:30', 12, null, null, 'Spring', 2024),

('CSCI', 6221, 'M', '15:00', '17:30', 13, null, null, 'Summer', 2024),
('CSCI', 6461, 'T', '15:00', '17:30', 5, null, null, 'Summer', 2024),
('CSCI', 6212, 'W', '15:00', '17:30', 5, null, null, 'Summer', 2024),
('CSCI', 6232, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('CSCI', 6233, 'T', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('CSCI', 6241, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('CSCI', 6242, 'R', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('CSCI', 6246, 'T', '15:00', '17:30', 13, null, null, 'Summer', 2024),
('CSCI', 6251, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('CSCI', 6254, 'M', '15:00', '17:30', 13, null, null, 'Summer', 2024),
('CSCI', 6260, 'R', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('CSCI', 6262, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('CSCI', 6283, 'T', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('CSCI', 6284, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('CSCI', 6286, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('CSCI', 6384, 'W', '15:00', '17:30', 13, null, null, 'Summer', 2024),
('ECE', 6241, 'M', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('ECE', 6242, 'T', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('MATH', 6210, 'W', '18:00', '20:30', 13, null, null, 'Summer', 2024),
('CSCI', 6339, 'R', '16:00', '18:30', 13, null, null, 'Summer', 2024),

('CSCI', 6221, 'M', '15:00', '17:30', 14, null, null, 'Fall', 2024),
('CSCI', 6461, 'T', '15:00', '17:30', 5, null, null, 'Fall', 2024),
('CSCI', 6212, 'W', '15:00', '17:30', 5, null, null, 'Fall', 2024),
('CSCI', 6232, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('CSCI', 6233, 'T', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('CSCI', 6241, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('CSCI', 6242, 'R', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('CSCI', 6246, 'T', '15:00', '17:30', 14, null, null, 'Fall', 2024),
('CSCI', 6251, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('CSCI', 6254, 'M', '15:00', '17:30', 14, null, null, 'Fall', 2024),
('CSCI', 6260, 'R', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('CSCI', 6262, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('CSCI', 6283, 'T', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('CSCI', 6284, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('CSCI', 6286, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('CSCI', 6384, 'W', '15:00', '17:30', 14, null, null, 'Fall', 2024),
('ECE', 6241, 'M', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('ECE', 6242, 'T', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('MATH', 6210, 'W', '18:00', '20:30', 14, null, null, 'Fall', 2024),
('CSCI', 6339, 'R', '16:00', '18:30', 14, null, null, 'Fall', 2024);

"""
cursor.execute(query)

query = """
INSERT INTO schedule (course_dept, course_num, schedule_day, start_time, end_time, instructor_id, room, room_capacity, semester, year) VALUES
('CSCI', 6220, 'R', '16:00', '18:30', 14, null, null, 'Fall', 2024),
('CSCI', 6220, 'R', '16:00', '18:30', 14, null, null, 'Fall', 2023),
('CSCI', 6220, 'R', '16:00', '18:30', 14, null, null, 'Fall', 2022),
('CSCI', 6325, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2024),
('CSCI', 6325, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2023),
('CSCI', 6325, 'M', '18:00', '20:30', 12, null, null, 'Spring', 2022);
"""
cursor.execute(query)

#END OF COURSE AND PREREQUISITE INSERTIONS#

#THE FOLLOWING CODE INSERTS A TEST APPLICATION FOR THE TEST APPLICANT USER WITH ASSOCIATED TABLES#

query = """
INSERT INTO transcript 
(transcriptid, user_id, transcriptstatus)
VALUES
(1, 9, 'not received')
"""
cursor.execute(query)

query = """
INSERT INTO recommendationletter 
(letterid, user_id, rec_name_one, rec_email_one, rec_letter_one, status_one, code, all_received)
VALUES
(1, 9, 'John Park', 'wizgm8@gmail.com', 'very good student', 'received', '2024-04-29 17:25:09.570334', 'received')
"""
cursor.execute(query)

query = """
INSERT INTO priordegrees 
(applicationid, user_id, degree_type, year, gpa, school, major)
VALUES
(1, 9, 'BS', '2004', '3.00', 'George Washington University', 'Computer Science')
"""
cursor.execute(query)

query = """
INSERT INTO application 
(applicationid, user_id, status, decision, timestamp, firstname, lastname, address, ssn, phonenumber, degreessought, areas_interest, priordegrees, uid, semester, year, transcript_submission, transcript_submission_received)
VALUES
(1, 9, 'application complete and under review', 'undecided', '2024-04-29', 'fapplicant', 'lapplicant', '123 Admin St., City, State 00000', '111-99-1111', '224-221-1575', 'MS', 'Computer Science', 'BS', '00000002', 'Fall', '2025', 'mail', 'received')
"""
cursor.execute(query)

#END OF TEST APPLICANT APPLICATION

#FOLLOWING CODE INSERTS REQUIREMENTS TO GRADUATE#

query = """
INSERT INTO MS_requirements VALUES
('3.0', 30, 2, 2);
"""
cursor.execute(query)

query = """
INSERT INTO MS_required_courses VALUES
('CSCI', 6221, 'SW Paradigms', 3),
('CSCI', 6212, 'Algorithms', 3),
('CSCI', 6461, 'Computer Architecture', 3);
"""
cursor.execute(query)

query = """
INSERT INTO PhD_requirements VALUES
('3.5', 36, 30, 1, 0);
"""
cursor.execute(query)

query = """
INSERT INTO PhD_required_courses VALUES
('CSCI', 6221, 'SW Paradigms', 3),
('CSCI', 6212, 'Algorithms', 3),
('CSCI', 6461, 'Computer Architecture', 3);
"""
cursor.execute(query)

#END OF INSERTION FOR GRADUATION REQUIREMENTS#

#INSERT FOR ALUMNI FOR TEST USER#
query = """
INSERT INTO alumni (university_id, user_id, year_of_graduation, program, major, gpa) VALUES
('99999998', 8, 2024, 'MS', 'Computer Science', '4.00');
"""
cursor.execute(query)

query = """
INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, year, grade, crn) VALUES
('99999998', 'CSCI', 6212, 'Algorithms', 3, 'Fall', 2023, 'A', '31939621211'),
('99999998', 'CSCI', 6241, 'Database 1', 3, 'Fall', 2023, 'A', '31939621211'),
('99999998', 'CSCI', 6220, 'Machine Learning', 3, 'Fall', 2023, 'A', '31939621211');
"""
cursor.execute(query)

query = """
INSERT INTO forms (form_id, submitted_university_id, approved) VALUES
(1, '99999998', 1);
"""
cursor.execute(query)

query = """
INSERT INTO forms_classes (form_id, university_id, dept, course_num, credits) VALUES
(1, '99999998', 'CSCI', 6212, 3),
(1, '99999998', 'CSCI', 6241, 3),
(1, '99999998', 'CSCI', 6220, 3);
"""
cursor.execute(query)

query = """
INSERT INTO graduation_application (form_id, submitted_university_id, approved) VALUES
(1, '99999998', 1);
"""
cursor.execute(query)

#END OF INSERTION FOR ALUMNI#


#DEMO DAY#


# REGS #
query = """
INSERT INTO user VALUES 
(17, 'bholiday@gwu.edu','billie123', 'pass', 'Billie', 'Holiday', '2000-01-01', '123 House','grad_stu'),
(18, 'dkrall@gwu.edu','diana123','pass','Diana', 'Krall', '2000-01-01', '123 Building', 'grad_stu'),
(19, 'secretary@gwu.edu','regsec123','pass','REGSEC', 'rg', '2000-01-01', '256 Road', 'grad_sec'),
(20, 'narahari@gwu.edu','Narahari123','pass','Bhagirath', 'Narahari', '1999-01-01', 'SEH 5800', 'instructor'),
(21, 'hchoi@gwu.edu','Choi123','pass','Hyeong-Ah', 'Choi', '1999-01-01', 'SEH 5850', 'instructor');
"""
cursor.execute(query)

query = """
INSERT INTO student 
(uid, user_id, advisor_id, program, major, gpa, cleared)
VALUES
('88888888', 17, 3, 'MS', 'Computer Science', '0.0', 0),
('99999999', 18, 3, 'MS', 'Computer Science', '0.0', 0);
"""
cursor.execute(query)

query = """
INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, year, grade, crn) VALUES
('88888888', 'CSCI', 6461, 'Computer Architecture', 3, 'Fall', 2023, 'IP', '31939621211'),
('88888888', 'CSCI', 6212, 'Algorithms', 3, 'Fall', 2023, 'IP', '31939646112');
"""
cursor.execute(query)

query = """
INSERT INTO forms (form_id, submitted_university_id, approved) VALUES
(2, '88888888', 1);
"""
cursor.execute(query)

query = """
INSERT INTO forms_classes (form_id, university_id, dept, course_num, credits) VALUES
(17, '88888888', 'CSCI', 6461, 3),
(17, '88888888', 'CSCI', 6212, 3);
"""
cursor.execute(query)

# APPS #



query = """
INSERT INTO user VALUES 
(29, 'starr@gwu.edu','starr111', 'pass', 'RINGO', 'StarrAPPS', '2000-01-01', '123 House','applicant'),
(30, 'john@gwu.edu','john12132','pass','John', 'Lennon', '1999-01-01', 'SEH 5850', 'applicant'),
(31, 'APPSnarahrai@gwu.edu','nara123','pass','NarahariReviewer', 'Narahari', '1999-01-01', 'SEH 5850', 'reviewer');
"""
cursor.execute(query)

#STARR APP#

query = """
INSERT INTO transcript 
(transcriptid, user_id, transcriptstatus)
VALUES
(2, 29, 'not received')
"""
cursor.execute(query)

query = """
INSERT INTO recommendationletter 
(letterid, user_id, rec_name_one, rec_email_one, rec_letter_one, status_one, code, all_received)
VALUES
(2, 29, 'John John', 'wizgm8@gmail.com', 'very good student', 'received', '2024-04-29 17:25:09.570334', 'received')
"""
cursor.execute(query)

query = """
INSERT INTO priordegrees 
(applicationid, user_id, degree_type, year, gpa, school, major)
VALUES
(2, 29, 'BS', '2004', '3.00', 'George Washington University', 'Computer Science')
"""
cursor.execute(query)

query = """
INSERT INTO application 
(applicationid, user_id, status, decision, timestamp, firstname, lastname, address, ssn, phonenumber, degreessought, areas_interest, priordegrees, uid, semester, year, transcript_submission, transcript_submission_received)
VALUES
(2, 29, 'application complete and under review', 'undecided', '2024-04-29', 'RINGO', 'StarrAPPS', '123 House', '222-11-1111', '224-221-1125', 'MS', 'Computer Science', 'BS', '66666667', 'Fall', '2025', 'mail', 'not received')
"""
cursor.execute(query)


#END OF STARR#

#JOHN APP#

query = """
INSERT INTO transcript 
(transcriptid, user_id, transcriptstatus)
VALUES
(3, 30, 'received')
"""
cursor.execute(query)

query = """
INSERT INTO recommendationletter 
(letterid, user_id, rec_name_one, rec_email_one, rec_letter_one, status_one, code, all_received)
VALUES
(3, 30, 'Peter Piper', 'wizgm8@gmail.com', 'very awesome student', 'received', '2024-04-29 17:25:09.570334', 'received')
"""
cursor.execute(query)

query = """
INSERT INTO priordegrees 
(applicationid, user_id, degree_type, year, gpa, school, major)
VALUES
(3, 30, 'BS', '2004', '4.00', 'George Washington University', 'Computer Science')
"""
cursor.execute(query)

query = """
INSERT INTO application 
(applicationid, user_id, status, decision, timestamp, firstname, lastname, address, ssn, phonenumber, degreessought, areas_interest, priordegrees, uid, semester, year, transcript_submission, transcript_submission_received)
VALUES
(3, 30, 'application complete and under review', 'undecided', '2024-04-29', 'John', 'Lennon', '123 House', '111-11-1111', '224-251-1575', 'MS', 'Computer Science', 'BS', '12312312', 'Fall', '2025', 'mail', 'received')
"""
cursor.execute(query)


#END OF JOHN#

# ADS #

#McCartney, Paul#
query = """
INSERT INTO user VALUES 
(22, 'paul@gwu.edu','paul123', 'pass', 'Paul', 'McCartney', '2000-01-01', 123 House,'grad_stu'),
(23, 'george@gwu.edu','George123','pass','George', 'Harrison', '2000-01-01', 123 Building, 'grad_stu'),
(24, 'ringo@gwu.edu','Ringo123','pass','Ringo', 'Starr', '2000-01-01', '256 Road', 'grad_stu'),
(25, 'eric@gwu.edu','Clapton123','pass','Clapton', 'Eric', '1999-01-01', 'SEH 5800', 'alumni'),
(26, 'ADSGS@gwu.edu','ADSGS123','pass','Bobby', 'ADSBOBBY', '1999-01-01', 'SEH 5850', 'grad_sec'),
(27, 'narahari@gwu.edu','Narahari123','pass','Bhagirath', 'Narahari', '1999-01-01', 'SEH 5800', 'fac_adv'),
(28, 'parmer@gwu.edu','Parmer123','pass','Parmer', 'Gabe', '1999-01-01', 'SEH 5850', 'fac_adv');
"""
cursor.execute(query)
query = """
INSERT INTO student 
(uid, user_id, advisor_id, program, major, gpa, cleared)
VALUES
('55555555', 22, 27, 'MS', 'Computer Science', '3.5', 0),
('66666666', 23, 28, 'MS', 'Computer Science', '2.9', 0),
('98765432', 24, 28, 'PhD', 'Computer Science', '4.0', 0);
"""
cursor.execute(query)

query = """
INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, year, grade, crn)
VALUES 
('55555555', 'CSCI', 6221, 'SW Paradigms', 3, 'Fall', 2023,'A', 31939622112),
('55555555', 'CSCI', 6212, 'Algorithms', 3, 'Fall',2023, 'A', 31939621212),
('55555555', 'CSCI', 6461, 'Computer Architecture', 3, 'Fall', 2023,'A', 31939646112),
('55555555', 'CSCI', 6232, 'Networks 1', 3, 'Fall',2023, 'A', 31939623212),
('55555555', 'CSCI', 6233, 'Networks 2', 3, 'Fall',2023, 'A', 31939623312),
('55555555', 'CSCI', 6241, 'Database 1', 3, 'Fall',2023, 'B', 31939624112),
('55555555', 'CSCI', 6246, 'Compilers', 3, 'Fall',2023, 'B', 31939624612),
('55555555', 'CSCI', 6262, 'Graphics 1', 3, 'Fall',2023, 'B', 31939626212),
('55555555', 'CSCI', 6283, 'Security 1', 3, 'Fall',2023, 'B', 31939628312),
('55555555', 'CSCI', 6242, 'Database 2', 3, 'Fall',2023, 'B', 31939624212);
"""
cursor.execute(query)

query = """
INSERT INTO forms (form_id, submitted_university_id, approved) VALUES
(3, '55555555', 22);
"""
cursor.execute(query)

query = """
INSERT INTO forms_classes (form_id, university_id, dept, course_num, credits) VALUES
(3, '55555555', 'CSCI', 6221, 3),
(3,'55555555', 'CSCI', 6212, 3),
(3,'55555555', 'CSCI', 6461, 3),
(3,'55555555', 'CSCI', 6232, 3),
(3,'55555555', 'CSCI', 6233, 3),
(3,'55555555', 'CSCI', 6241, 3),
(3,'55555555', 'CSCI', 6246, 3),
(3,'55555555', 'CSCI', 6262, 3),
(3,'55555555', 'CSCI', 6283, 3),
(3,'55555555', 'CSCI', 6242, 3);
"""
cursor.execute(query)



query = """
INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, year, grade, crn)
VALUES 
('66666666', 'ECE', 6242, 'Information Theory', 3, 'Fall', 2023,'C', 535-64624212),
('66666666', 'CSCI', 6221, 'SW Paradigms', 3, 'Fall',2023,'B', 31939622112),
('66666666', 'CSCI', 6461, 'Computer Architecture', 3, 'Fall',2023, 'B', 31939646112),
('66666666', 'CSCI', 6212, 'Algorithms', 3, 'Fall', 2023,'B', 31939621212),
('66666666', 'CSCI', 6232, 'Networks 1', 3, 'Fall', 2023,'B', 31939623212),
('66666666', 'CSCI', 6233, 'Networks 2', 3, 'Fall', 2023,'B', 31939623312),
('66666666', 'CSCI', 6241, 'Database 1', 3, 'Fall', 2023,'B', 31939624112),
('66666666', 'CSCI', 6242, 'Database 2', 3, 'Fall', 2023,'B', 31939624212),
('66666666', 'CSCI', 6283, 'Security 1', 3, 'Fall', 2023,'B', 31939628312),
('66666666', 'CSCI', 6284, 'Cryptography', 3, 'Fall' , 2023,'B', 31939628412);
"""
cursor.execute(query)

query = """
INSERT INTO forms (form_id, submitted_university_id, approved) VALUES
(4, '66666666', 23);
"""
cursor.execute(query)

query = """
INSERT INTO forms_classes (form_id, university_id, dept, course_num, credits) VALUES
(4, '66666666', 'CSCI', 6221, 3),
(4,'66666666', 'CSCI', 6212, 3),
(4,'66666666', 'CSCI', 6461, 3),
(4,'66666666', 'CSCI', 6232, 3),
(4,'66666666', 'CSCI', 6232, 3),
(4,'66666666', 'CSCI', 6233, 3),
(4,'66666666', 'CSCI', 6241, 3),
(4,'66666666', 'CSCI', 6242, 3),
(4,'66666666', 'CSCI', 6283, 3),
(4,'66666666', 'CSCI', 6284, 3);
"""
cursor.execute(query)


query = """
INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, year, grade, crn)
VALUES ('12345678', 'CSCI', 6221, 'SW Paradigms', 3, 'Fall',  2023,'A', 31939622112),
('98765432', 'CSCI', 6461, 'Computer Architecture', 3, 'Fall',  2023,'A', 31939646112),
('98765432', 'CSCI', 6212, 'Algorithms', 3, 'Fall',2023, 'A', 31939621212),
('98765432', 'CSCI', 6220, 'Machine Learning', 3, 'Fall',  2023,'A', 31939622012),
('98765432', 'CSCI', 6232, 'Networks 1', 3, 'Fall', 2023, 'A', 31939623212),
('98765432', 'CSCI', 6233, 'Networks 2', 3, 'Fall', 2023, 'A', 31939623312),
('98765432', 'CSCI', 6241, 'Database 1', 3, 'Fall',  2023,'A', 31939624112),
('98765432', 'CSCI', 6242, 'Database 2', 3, 'Fall',  2023,'A', 31939624212),
('98765432', 'CSCI', 6246, 'Compilers', 3, 'Fall',  2023,'A', 31939624612),
('98765432', 'CSCI', 6260, 'Multimedia', 3, 'Fall',  2023,'A', 31939626012),
('98765432', 'CSCI', 6251, 'Cloud Computing', 3, 'Fall',  2023,'A', 31939625112),
('98765432', 'CSCI', 6254, 'SW Engineering', 3, 'Fall',  2023,'A', 31939625412);

"""
cursor.execute(query)

query = """
INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, year, grade, crn)
VALUES ('77777777', 'CSCI', 6221, 'SW Paradigms', 3, 'Fall', 2023,'B', 31939622112),
('77777777', 'CSCI', 6461, 'Computer Architecture', 3, 'Fall', 2023,'B', 31939646112),
('77777777', 'CSCI', 6212, 'Algorithms', 3, 'Fall', 2023,'B', 31939621212),
('77777777', 'CSCI', 6232, 'Networks 1', 3, 'Fall', 2023,'B', 31939623212),
('77777777', 'CSCI', 6233, 'Networks 2', 3, 'Fall',2023, 'B', 31939623312),
('77777777', 'CSCI', 6241, 'Database 1', 3, 'Fall', 2023,'B', 31939624112),
('77777777', 'CSCI', 6242, 'Database 2', 3, 'Fall', 2023,'B', 31939624212),
('77777777', 'CSCI', 6283, 'Security 1', 3, 'Fall', 2023,'A', 31939628312),
('77777777', 'CSCI', 6284, 'Cryptography', 3, 'Fall', 2023,'A', 31939628412),
('77777777', 'CSCI', 6286, 'Network Security', 3, 'Fall', 2023,'A', 31939628612);

"""
cursor.execute(query)

query = """
INSERT INTO alumni (university_id, user_id, year_of_graduation, program, major, gpa)
VALUES ('77777777', 14, 2014, 'MS', 'Computer Science', '3.3');
"""
cursor.execute(query)


db.commit()
cursor.close()
db.close()
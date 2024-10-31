DROP TABLE IF EXISTS user_credentials;
DROP TABLE IF EXISTS alumni;
DROP TABLE IF EXISTS course_taken;
DROP TABLE IF EXISTS thesis;
DROP TABLE IF EXISTS forms;
DROP TABLE IF EXISTS graduation_application;
DROP TABLE IF EXISTS forms_classes;
DROP TABLE IF EXISTS program;
DROP TABLE IF EXISTS MS_requirements;
DROP TABLE IF EXISTS MS_required_courses;
DROP TABLE IF EXISTS PhD_requirements;
DROP TABLE IF EXISTS PhD_required_courses;
DROP TABLE IF EXISTS application;
DROP TABLE IF EXISTS transcript;
DROP TABLE IF EXISTS recommendationletter;
DROP TABLE IF EXISTS reviewform;
DROP TABLE IF EXISTS schedule;
DROP TABLE IF EXISTS enrollment;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS prerequisite;



--ALL TABLES HERE ARE FROM ADS AND UNCHANGED--
CREATE TABLE IF NOT EXISTS alumni (
    -- student ID
    university_id       VARCHAR(20) NOT NULL,
    --user_id
    user_id             INTEGER NOT NULL,
    -- year of graduation
    year_of_graduation  INT(4) NOT NULL,
    -- degree role (MA, MS, PHD)
    program     VARCHAR(4) NOT NULL,
    -- what they studied
    major       VARCHAR(20),
    -- grade point average
    gpa                 VARCHAR(20) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_credentials (user_id)
);

CREATE TABLE IF NOT EXISTS course_taken (
    university_id       VARCHAR(20) NOT NULL,
    dept                VARCHAR(4) NOT NULL,
    course_num          INT NOT NULL,
    course_title        VARCHAR(20) NOT NULL,
    credits             INT NOT NULL,
    -- freshfall (0) / freshspri (1) / sophfall (2) / sophspri (3) / jf (4) / js (5) / sf (6) / ss (7)
    semester_taken      INT NOT NULL,
    grade               VARCHAR(2)
);
CREATE TABLE IF NOT EXISTS thesis (
    form_id                            INTEGER PRIMARY KEY AUTOINCREMENT,
    thesis                             TEXT,
    submitted_university_id            VARCHAR(20) NOT NULL,
    FOREIGN KEY (submitted_university_id) REFERENCES student (uid),  
    FOREIGN KEY (form_id) REFERENCES forms (form_id)
);
CREATE TABLE IF NOT EXISTS forms (
    form_id                            INTEGER PRIMARY KEY AUTOINCREMENT,
    submitted_university_id            VARCHAR(20) NOT NULL,
    approved                           BIT DEFAULT 0,
    FOREIGN KEY (submitted_university_id) REFERENCES student (uid)
);
CREATE TABLE IF NOT EXISTS graduation_application (
    form_id                            INTEGER PRIMARY KEY AUTOINCREMENT,
    submitted_university_id            VARCHAR(20) NOT NULL,
    approved                           BIT DEFAULT 0,
    FOREIGN KEY (submitted_university_id) REFERENCES student (uid)
);
CREATE TABLE IF NOT EXISTS forms_classes (
    form_id             INTEGER,
    university_id       VARCHAR(20) NOT NULL,
    dept                VARCHAR(4) NOT NULL,
    course_num          INT NOT NULL,
    FOREIGN KEY (dept) REFERENCES course (dept),
    FOREIGN KEY (course_num) REFERENCES course (course_num)
);
CREATE TABLE IF NOT EXISTS program (
    program_id INT NOT NULL,
    program_field VARCHAR(20) NOT NULL,
    program_degree VARCHAR(4) NOT NULL,
    program_gpa_min FLOAT NOT NULL,
    credit_hrs INT NOT NULL,
    -- neccessary credits in program
    credit_hrs_prgm INT NOT NULL,
    -- most courses outside of program that will count towards degree
    courses_non_prgm INT NOT NULL,
    below_b INT NOT NULL,
    thesis BIT NOT NULL
);
CREATE TABLE IF NOT EXISTS MS_requirements(
    min_gpa                         VARCHAR(20),
    min_credit_hours                INTEGER,
    most_courses_outside_CS         INTEGER,
    most_grades_below_B               INTEGER
);
CREATE TABLE IF NOT EXISTS MS_required_courses(
    dept                VARCHAR(4) NOT NULL,
    course_num          INT NOT NULL,
    course_title        VARCHAR(20) NOT NULL,
    credits             INT NOT NULL
);
CREATE TABLE IF NOT EXISTS PhD_requirements(
    min_gpa                         VARCHAR(20),
    min_credit_hours                INTEGER,
    min_credits_in_cs               INTEGER,
    most_grades_below_B             INTEGER,
    pass_thesis_Defense             BIT NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS PhD_required_courses(
    dept                VARCHAR(4) NOT NULL,
    course_num          INT NOT NULL,
    course_title        VARCHAR(20) NOT NULL,
    credits             INT NOT NULL
);
--END OF TABLES FROM ADS THAT ARE UNCHANGED--
--ALL TABLES HERE ARE FROM APPS AND UNCHANGED--
CREATE TABLE application (
    applicationid INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INT, 
    status TEXT CHECK(status IN ('application incomplete', 'application complete and under review','decision', NULL)) DEFAULT NULL,
    decision TEXT CHECK(decision IN ('admit', 'admit with aid', 'reject', 'undecided', NULL)) DEFAULT NULL,
    timestamp date NOT NULL, 

    -- Personal Info 

    name VARCHAR(255),
    address VARCHAR(255),
    ssn VARCHAR(255),
    phonenumber VARCHAR(255),

    -- Academic Info 

    degreessought TEXT CHECK(degreessought IN ('MS','PHD', NULL)) DEFAULT NULL,
    priordegrees TEXT CHECK(priordegrees IN ('BS','MS', NULL)) DEFAULT NULL,
    greverbal int(3),
    grequantitative int(3),
    priorwork VARCHAR(255),

    FOREIGN KEY (userid) REFERENCES user(userid)
);

CREATE TABLE transcript (
    transcriptid INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INT,
    transcriptstatus TEXT CHECK(transcriptstatus IN ('received', 'not received')) DEFAULT 'not received',

    FOREIGN KEY (userid) REFERENCES user(userid)
);

CREATE TABLE recommendationletter (
    letterid INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INT,
    recname VARCHAR(100) NOT NULL,
    recemail VARCHAR(100) NOT NULL,

    FOREIGN KEY (userid) REFERENCES user(userid)
);

CREATE TABLE reviewform (

    reviewid INTEGER PRIMARY KEY AUTOINCREMENT,
    reviewerid VARCHAR(255),
    userid INT,
    finaldecision TEXT CHECK (finaldecision IN ('reject', 'borderline admit', 'admit without aid', 'admit with aid','undecided')) DEFAULT 'undecided',
    comments VARCHAR(255),
    recommendedadvisor VARCHAR(100),

    -- AppName <Last Name, First Name> 
    -- StuNum  <8 digits>

    FOREIGN KEY (userid) REFERENCES user(userid),
    FOREIGN KEY (reviewerid) REFERENCES user(userid),
    FOREIGN KEY (reviewid) REFERENCES application(applicationid)
); 
--END OF TABLES FROM APPS THAT ARE UNCHANGED--

--ALL TABLES HERE ARE FROM REGS AND UNCHANGED--
CREATE TABLE schedule (
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
  crn           varchar(20) GENERATED ALWAYS AS (
    
        CAST(UNICODE(SUBSTRING(course_dept, 1, 1)) - UNICODE('A') + 1 AS CHAR) ||
        CAST(UNICODE(SUBSTRING(course_dept, 2, 1)) - UNICODE('A') + 1 AS CHAR) ||
        CAST(UNICODE(SUBSTRING(course_dept, 3, 1)) - UNICODE('A') + 1 AS CHAR) ||
        CAST(UNICODE(SUBSTRING(course_dept, 4, 1)) - UNICODE('A') + 1 AS CHAR) ||
        course_num ||
        CASE semester
            WHEN 'Fall' THEN '1'
            WHEN 'Spring' THEN '2'
            WHEN 'Summer' THEN '3'
        END ||
        year - 2021
    
  ) STORED,

  primary key (course_dept, course_num, semester, year),
  foreign key (course_dept, course_num) references course(department, course_num),
  foreign key (instructor_id) references user(uid)
);
CREATE TABLE enrollment (
  student_uid  INTEGER not null,
  crn          varchar(20) not null,
  grade        varchar(2) DEFAULT 'IP' CHECK(grade IN ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP')),

  primary key (student_uid, crn),
  foreign key (student_uid) references student(uid),
  foreign key (crn) references schedule(crn)
);
--END OF TABLES FROM REGS THAT ARE UNCHANGED--

--THE FOLLOWING TABLES HAVE BEEN MODIFIED FROM ADS, REGS, APPS--
--from_what_database: original_table_name

--ADS: user--
--REGS: user--
--APPS: user--
CREATE TABLE IF NOT EXISTS user(
    user_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    email               varchar(50)  NOT NULL UNIQUE,
    username            varchar(50) NOT NULL,
    password            varchar(50) NOT NULL,
    first_name          VARCHAR(20),
    last_name           VARCHAR(20),
    dob                 date,
    address             VARCHAR(20),
    role                VARCHAR(20) CHECK(role IN ('admin', 'grad_sec', 'fac_adv', 'reviewer', 'instructor', 'grad_stu', 'alumni', 'applicant', 'user')) DEFAULT 'user'
);

--ADS: student--
--REGS: student--
CREATE TABLE IF NOT EXISTS student(
    uid                 VARCHAR(20) UNIQUE,
    user_id             INTEGER UNIQUE,
    advisor_id          INTEGER,
    program             VARCHAR(20) CHECK(program IN ('MS', 'PhD')),
    major               VARCHAR(20),
    gpa                 VARCHAR(20),
    cleared             BIT DEFAULT 0
);

--ADS: course--
--REGS: course--
CREATE TABLE IF NOT EXISTS course (
    department          VARCHAR(4) NOT NULL,
    course_num          INT NOT NULL,
    title               VARCHAR(20) NOT NULL,
    credit              INT NOT NULL
);
--ADS: prerequisite--
--REGS: prerequisite--
CREATE TABLE IF NOT EXISTS prerequisite (
    course_dep          VARCHAR(4),
    course_num          INT,
    prereq_dep          VARCHAR(4),
    prereq_num          INT NOT NULL,
    foreign key (course_dep, course_num) references course(department, course_num),
    foreign key (prereq_dep, prereq_num) references course(department, course_num)
);
--END OF TABLES FROM DATABASE THAT HAVE BEEN MODIFIED--





























--DEMO TEST STARTING STATE--

--START OF PhD_required_courses TABLE--
INSERT INTO PhD_required_courses VALUES
('CSCI', 6221, 'SW Paradigms', 3),
('CSCI', 6212, 'Algorithms', 3),
('CSCI', 6461, 'Computer Architecture', 3);
--END OF PhD_required_courses TABLE--
--START OF PhD_requirements TABLE--
INSERT INTO PhD_requirements VALUES
('3.5', 36, 30, 1, 0);
--END OF PhD_requirements TABLE--
--START OF MS_required_courses TABLE--
INSERT INTO MS_required_courses VALUES
('CSCI', 6221, 'SW Paradigms', 3),
('CSCI', 6212, 'Algorithms', 3),
('CSCI', 6461, 'Computer Architecture', 3);
--END OF MS_required_courses TABLE--
--START OF MS_requirements TABLE--
INSERT INTO MS_requirements VALUES
('3.0', 30, 2, 2);
--END OF MS_requirements TABLE--

-- Inserting courses into the course table
INSERT INTO course VALUES
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

INSERT INTO prerequisite VALUES
('CSCI', 6233, 'CSCI', 6232),
('CSCI', 6246, 'CSCI', 6461),
('CSCI', 6246, 'CSCI', 6461),
('CSCI', 6246, 'CSCI', 6212),
('CSCI', 6251, 'CSCI', 6461),
('CSCI', 6254, 'CSCI', 6221),
('CSCI', 6283, 'CSCI', 6212),
('CSCI', 6284, 'CSCI', 6212),
('CSCI', 6286, 'CSCI', 6283),
('CSCI', 6286, 'CSCI', 6232),
('CSCI', 6325, 'CSCI', 6212),
('CSCI', 6339, 'CSCI', 6461),
('CSCI', 6339, 'CSCI', 6212),
('CSCI', 6384, 'CSCI', 6284);

--McCartney, Paul--
INSERT INTO user_credentials (user, pass, user_id) 
VALUES ('pauluser', 'paulpass', 11);
INSERT INTO user (first_name, last_name, role, email, address, user_id)
VALUES ('Paul', 'McCartney', 'grad_stu', 'pmc@gwu.edu', 'J William Fullbright Hall', 11);
INSERT INTO student (uid, user_id, advisor_id, program, major, cleared, gpa)
VALUES ('55555555', 11, 16, 'MS', 'Computer Science', 0, '3.5');
INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, grade)
VALUES ('55555555', 'CSCI', 6221, 'SW Paradigms', 3, 4, 'A'),
('55555555', 'CSCI', 6212, 'Algorithms', 3, 4, 'A'),
('55555555', 'CSCI', 6461, 'Computer Architecture', 3, 4, 'A'),
('55555555', 'CSCI', 6232, 'Networks 1', 3, 4, 'A'),
('55555555', 'CSCI', 6233, 'Networks 2', 3, 4, 'A'),
('55555555', 'CSCI', 6241, 'Database 1', 3, 4, 'B'),
('55555555', 'CSCI', 6246, 'Compilers', 3, 4, 'B'),
('55555555', 'CSCI', 6262, 'Graphics 1', 3, 4, 'B'),
('55555555', 'CSCI', 6283, 'Security 1', 3, 4, 'B'),
('55555555', 'CSCI', 6242, 'Database 2', 3, 4, 'B');

--Harrison, George--
INSERT INTO user_credentials (user, pass, user_id) 
VALUES ('georgeuser', 'georgepass', 12);
INSERT INTO user (first_name, last_name, role, email, address, user_id)
VALUES ('George', 'Harrison', 'grad_stu', 'gh@gwu.edu', 'J William Fullbright Hall', 12);
INSERT INTO student (uid, user_id, advisor_id, program, major, cleared, gpa)
VALUES ('66666666', 12, 17, 'MS', 'Computer Science', 0, '2.9');
INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, grade)
VALUES ('66666666', 'ECE', 6242, 'Information Theory', 3, 4, 'C'),
('66666666', 'CSCI', 6221, 'SW Paradigms', 3, 4, 'B'),
('66666666', 'CSCI', 6461, 'Computer Architecture', 3, 4, 'B'),
('66666666', 'CSCI', 6212, 'Algorithms', 3, 4, 'B'),
('66666666', 'CSCI', 6232, 'Networks 1', 3, 4, 'B'),
('66666666', 'CSCI', 6233, 'Networks 2', 3, 4, 'B'),
('66666666', 'CSCI', 6241, 'Database 1', 3, 4, 'B'),
('66666666', 'CSCI', 6242, 'Database 2', 3, 4, 'B'),
('66666666', 'CSCI', 6283, 'Security 1', 3, 4, 'B'),
('66666666', 'CSCI', 6284, 'Cryptography', 3, 4 , 'B');

--Starr, Ringo--
INSERT INTO user_credentials (user, pass, user_id) 
VALUES ('ringouser', 'ringopass', 13);
INSERT INTO user (first_name, last_name, role, email, address, user_id)
VALUES ('Ringo', 'Starr', 'grad_stu', 'rs@gwu.edu', 'SEAS', 13);
INSERT INTO student (uid, user_id, advisor_id, program, major, cleared, gpa)
VALUES ('12345678', 13, 17, 'PhD', 'Computer Science', 0, '4.0');
INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, grade)
VALUES ('12345678', 'CSCI', 6221, 'SW Paradigms', 3, 4, 'A'),
('12345678', 'CSCI', 6461, 'Computer Architecture', 3, 4, 'A'),
('12345678', 'CSCI', 6212, 'Algorithms', 3, 4, 'A'),
('12345678', 'CSCI', 6220, 'Machine Learning', 3, 4, 'A'),
('12345678', 'CSCI', 6232, 'Networks 1', 3, 4, 'A'),
('12345678', 'CSCI', 6233, 'Networks 2', 3, 4, 'A'),
('12345678', 'CSCI', 6241, 'Database 1', 3, 4, 'A'),
('12345678', 'CSCI', 6242, 'Database 2', 3, 4, 'A'),
('12345678', 'CSCI', 6246, 'Compilers', 3, 4, 'A'),
('12345678', 'CSCI', 6260, 'Multimedia', 3, 4, 'A'),
('12345678', 'CSCI', 6251, 'Cloud Computing', 3, 4, 'A'),
('12345678', 'CSCI', 6254, 'SW Engineering', 3, 4, 'A');

--Clapton, Eric--
INSERT INTO user_credentials (user, pass, user_id) 
VALUES ('ericuser', 'ericpass', 14);
INSERT INTO user (first_name, last_name, role, email, address, user_id)
VALUES ('Eric', 'Clapton', 'alumni', 'ec@gwu.edu', '123 House in Chicago', 14);
INSERT INTO alumni (university_id, user_id, year_of_graduation, program, major, gpa)
VALUES ('77777777', 14, 2014, 'MS', 'Computer Science', '3.3');
INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, grade)
VALUES ('77777777', 'CSCI', 6221, 'SW Paradigms', 3, 4, 'B'),
('77777777', 'CSCI', 6461, 'Computer Architecture', 3, 4, 'B'),
('77777777', 'CSCI', 6212, 'Algorithms', 3, 4, 'B'),
('77777777', 'CSCI', 6232, 'Networks 1', 3, 4, 'B'),
('77777777', 'CSCI', 6233, 'Networks 2', 3, 4, 'B'),
('77777777', 'CSCI', 6241, 'Database 1', 3, 5, 'B'),
('77777777', 'CSCI', 6242, 'Database 2', 3, 5, 'B'),
('77777777', 'CSCI', 6283, 'Security 1', 3, 6, 'A'),
('77777777', 'CSCI', 6284, 'Cryptography', 3, 6, 'A'),
('77777777', 'CSCI', 6286, 'Network Security', 3, 6, 'A');

--Perry, Katy--
INSERT INTO user_credentials (user, pass, user_id) 
VALUES ('katyuser', 'katypass', 15);
INSERT INTO user (first_name, last_name, role, email, address, user_id)
VALUES ('Katy', 'Perry', 'grad_sec', 'kp@gwu.edu', '9570 Hidden Valley Road, Beverly Hills, California', 15);


--Narahari, Bhagirath--
INSERT INTO user_credentials (user, pass, user_id) 
VALUES ('narahariuser', 'naraharipass', 16);
INSERT INTO user (first_name, last_name, role, email, address, user_id)
VALUES ('Bhagirath', 'Narahari', 'fac_adv', 'bn@gwu.edu', 'SEAS', 16);


--Parmer , Gabriel--
INSERT INTO user_credentials (user, pass, user_id) 
VALUES ('parmeruser', 'parmerpass', 17);
INSERT INTO user (first_name, last_name, role, email, address, user_id)
VALUES ('Gabriel', 'Parmer', 'fac_adv', 'gp@gwu.edu', 'SEAS', 17);

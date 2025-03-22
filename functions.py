"""
these will be all the functions that we need for main.py
"""

from flask import Flask
import sqlite3
import random
import mysql.connector
import mysql.connector.cursor
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from email.header import decode_header
import os
from werkzeug.utils import secure_filename

sender_email = "amzgwu@gmail.com"
password = "yosj bbse rxzq pfna"
imap_server = "imap.gmail.com"

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = '/static/transcript'

def connect_db():
    """connect to the mysql database"""
    db = mysql.connector.connect(
        host="amz-integration-phase2.crso3uorc9sy.us-east-1.rds.amazonaws.com",
        user="admin",
        passwd="amzamzamz",
        database="university",
        autocommit=True,
    )
    return db
def application_stats(apps) -> dict:
    stats = {
        'total_apps': 0,
        'admitted_without_aid': 0,
        'admitted_with_aid': 0,
        'rejected':0,
        'undecided':0,
        'ms':0,
        'phd':0
    }

    for app in apps:
        stats['total_apps'] += 1
        if app['decision'] == 'admit':
            stats['admitted_without_aid'] += 1
        if app['decision'] == 'admit with aid':
             stats['admitted_with_aid'] += 1
        if app['decision'] == 'reject':
             stats['rejected'] += 1
        if app['decision'] == 'undecided':
             stats['undecided'] += 1
        if app['degreessought'] == 'MS':
            stats['ms'] += 1
        if app['degreessought'] == 'PhD':
            stats['phd'] += 1
    return stats

def remove_course_crn(crn: str, db: mysql.connector.MySQLConnection):

    cursor = db.cursor(dictionary=True)

    cursor.execute("DELETE FROM schedule WHERE crn = %s", (crn,))

    db.commit()

    return


def filter_students_cleared_graduate(db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student JOIN user ON student.user_id = user.user_id WHERE student.cleared = 1")
    
    students = cursor.fetchall()

    return students
def filter_application_semester(filter: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM application LEFT JOIN transcript ON application.applicationid = transcript.transcriptid LEFT JOIN recommendationletter ON application.applicationid = recommendationletter.letterid WHERE application.semester = %s", (filter,)
    )
    filtered = cursor.fetchall()

    return filtered

def filter_application_year(filter: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM application LEFT JOIN transcript ON application.applicationid = transcript.transcriptid LEFT JOIN recommendationletter ON application.applicationid = recommendationletter.letterid WHERE application.year = %s", (filter,)
    )
    filtered = cursor.fetchall()

    return filtered

def filter_application_program(filter: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM application LEFT JOIN transcript ON application.applicationid = transcript.transcriptid LEFT JOIN recommendationletter ON application.applicationid = recommendationletter.letterid WHERE application.degreessought = %s", (filter,)
    )
    filtered = cursor.fetchall()

    return filtered

def filter_students_semester(filter: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM student JOIN application ON student.user_id = application.user_id WHERE application.semester = %s", (filter,)
    )
    filtered = cursor.fetchall()

    return filtered

def filter_students_year(filter: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM student JOIN application ON student.user_id = application.user_id WHERE application.year = %s", (filter,)
    )
    filtered = cursor.fetchall()

    return filtered

def filter_students_program(filter: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM student WHERE student.program = %s", (filter,)
    )
    filtered = cursor.fetchall()

    return filtered

def get_thesis(uid: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM thesis WHERE submitted_university_id = %s ORDER BY form_id DESC LIMIT 1", (uid,))

    thesis = cursor.fetchone()

    return thesis
def graduation_application_audit(student_information: dict, courses_taken, db: mysql.connector.MySQLConnection) -> str:
    program = student_information['program']
    requirements = get_requirements(program, db)

    if float(student_information['gpa']) < float(requirements['min_gpa']):
        audit = "GPA is too low!"
        return audit
    
    grades_below_B = 0
    for course in courses_taken:
        if grade_to_points(course['grade']) < 3 and course['grade'] != 'IP':
            grades_below_B += 1
        if course['grade'] == 'IP':
            audit = "You have courses in progress!"
            return audit
    if grades_below_B > requirements['most_grades_below_B']:
        audit = "Too many grades below B!"
        return audit

    audit = "Pass" 
    return audit

def add_course(dept: str, num: str, day: str, start: str, end: str, instructor: str, semester: str, year: str, db: mysql.connector.MySQLConnection):
    cursor = db.cursor(dictionary=True)

    cursor.execute("INSERT INTO schedule (course_dept, course_num, schedule_day, start_time, end_time, instructor_id, semester, year) VALUES (%s,  %s, %s,  %s, %s,  %s, %s,  %s)", (dept, num, day, start, end, instructor, semester, year))

    db.commit()

    return

def get_graduation_application(uid: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM graduation_application WHERE graduation_application.submitted_university_id = %s ORDER BY form_id DESC LIMIT 1", (uid,))
    grad_app = cursor.fetchone()
    return grad_app

def get_instructors(db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM user WHERE role = 'instructor'")

    instructors = cursor.fetchall()

    return instructors

def get_all_courses(db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM course")

    courses = cursor.fetchall()

    return courses

def course_reg_to_course(dept: str, num: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM course WHERE course.department = %s AND course.course_num = %s", (dept, num))
    course_info = cursor.fetchone()
    return course_info
def get_filtered_course_schedule(course_num: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM schedule WHERE course_num LIKE %s", ('%' + course_num + '%',))
    
    course_schedule = cursor.fetchall()

    return course_schedule

def phd_registration_check(course_schedule_registration: dict) -> bool:
    for course in course_schedule_registration:
        if course['course_num'] < 6000:
            return False
    return True

def get_requirements(program: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)
    if program == 'MS':
        cursor.execute("SELECT * FROM MS_requirements")

        requirements = cursor.fetchone()

    elif program == 'PhD':
        cursor.execute("SELECT * FROM PhD_requirements")

        requirements = cursor.fetchone()

    return requirements

def get_required_courses(program: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)
    if program == 'MS':
        cursor.execute("SELECT * FROM MS_required_courses")

        required_courses = cursor.fetchall()

    elif program == 'PhD':
        cursor.execute("SELECT * FROM PhD_required_courses")

        required_courses = cursor.fetchall()

    return required_courses

def get_student_by_instructor(user_id: str, uid: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    student_courses = get_courses_taken(uid, db)

    student_crn_courses = []

    for course in student_courses:
        student_crn_courses.append(course['crn'])

    instructor_courses = get_assigned_classes(user_id, db)


    matched = []

    for course in instructor_courses:
        for crn in student_crn_courses:
            if crn == course['crn']:
                matched.append(course)
    return matched
def get_all_students_by_instructor(user_id: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    assigned_classes = get_assigned_classes(user_id, db)

    cursor.execute("SELECT * FROM course_taken")

    student_courses = cursor.fetchall()

    all_students = []

    for course in assigned_classes:
        for student in student_courses:
            if course['crn'] == student['crn']:
                all_students.append(student)

    return all_students


def check_form_one(form_one, program: str, db: mysql.connector.MySQLConnection) -> str:
    required_courses = get_required_courses(program, db)
    requirements = get_requirements(program, db)

    for course in required_courses:
        found = 0
        for form_course in form_one:
            if course['course_title'] == form_course['title']:
                found = 1
        if found == 0:
            validate = 'Your Form 1 does not meet course requirements!'
            return validate
    
    total_credits = 0
    total_credits_cs = 0
    course_outside_cs = 0
    for course in form_one:
        total_credits += int(course['credit'])
        if course['department'] == 'CSCI':
            total_credits_cs += int(course['credit'])
        if not course['department'] == 'CSCI':
            course_outside_cs += 1
    
    if total_credits < requirements['min_credit_hours']:
        validate = 'Your Form 1 does not meet the minimum credit hours!'
        return validate
    
    if program == 'MS':
        if course_outside_cs > requirements['most_courses_outside_CS']:
            validate = 'Too many courses outside of CS!'
            return validate
    if program == 'PhD':
        if total_credits_cs < requirements['min_credits_in_cs']:
            validate = 'Too little credits in CS!'
            return validate

    validate = 'valid'
    return validate

def grade_to_points(grade:str) -> int:
    grade_points = {
        'A': 4.00,
        'A-': 3.70,
        'B+': 3.30,
        'B': 3.00,
        'B-': 2.70,
        'C+': 2.30,
        'C': 2.00,
        'C-': 1.70,
        'D+': 1.30,
        'D': 1.00,
        'D-': 0.70,
        'F': 0.00
    }
    return grade_points.get(grade, 0.00)


def update_gpa(uid: str, db: mysql.connector.MySQLConnection):
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM course_taken WHERE grade != 'IP' AND university_id = %s", (uid,))

    courses = cursor.fetchall()
    
    total_credits = 0
    total_grade_points = 0

    for course in courses:  
        total_credits += (int(course['credits']))
        grade_point = grade_to_points(course['grade']) * (int(course['credits']))
        total_grade_points += grade_point
    gpa = total_grade_points / total_credits
    gpa_rounded = round(gpa, 2)
    gpa_formatted = "{:.2f}".format(gpa_rounded)
    return gpa_formatted

def update_grade(uid: str, grade: str, crn: str, db: mysql.connector.MySQLConnection):
    cursor = db.cursor(dictionary=True)

    cursor.execute("UPDATE course_taken SET grade = %s WHERE university_id = %s AND crn = %s", (grade, uid, crn))

    updated_gpa = update_gpa(uid, db)

    cursor.execute("UPDATE student SET gpa = %s WHERE uid = %s", (updated_gpa, uid))

    db.commit()

    return
def check_overlap(course1, course2):
    start_time1, end_time1 = course1
    start_time2, end_time2 = course2
    
    # Check if start_time1 falls within the time interval of course2
    if start_time2 <= start_time1 < end_time2:
        return True
    
    # Check if end_time1 falls within the time interval of course2
    if start_time2 < end_time1 <= end_time2:
        return True
    
    return False
def overlap_check(course_schedule_registration: dict) -> bool:
    fallm22 = []
    fallm23 = []
    fallm24 = []
    springm22 = []
    springm23 = []
    springm24 = []
    summerm22 = []
    summerm23 = []
    summerm24 = []

    fallt22 = []
    fallt23 = []
    fallt24 = []
    springt22 = []
    springt23 = []
    springt24 = []
    summert22 = []
    summert23 = []
    summert24 = []

    fallw22 = []
    fallw23 = []
    fallw24 = []
    springw22 = []
    springw23 = []
    springw24 = []
    summerw22 = []
    summerw23 = []
    summerw24 = []

    fallr22 = []
    fallr23 = []
    fallr24 = []
    springr22 = []
    springr23 = []
    springr24 = []
    summerr22 = []
    summerr23 = []
    summerr24 = []

    fallf22 = []
    fallf23 = []
    fallf24 = []
    springf22 = []
    springf23 = []
    springf24 = []
    summerf22 = []
    summerf23 = []
    summerf24 = []
    for course in course_schedule_registration:
        if course['schedule_day'] == 'M' and course['semester'] == 'Fall' and course['year'] == 2022:
            fallm22.append(course)
        elif course['schedule_day'] == 'M' and course['semester'] == 'Fall' and course['year'] == 2023:
            fallm23.append(course)
        elif course['schedule_day'] == 'M' and course['semester'] == 'Fall' and course['year'] == 2024:
            fallm24.append(course)
        elif course['schedule_day'] == 'M' and course['semester'] == 'Spring' and course['year'] == 2022:
            springm22.append(course)
        elif course['schedule_day'] == 'M' and course['semester'] == 'Spring' and course['year'] == 2023:
            springm23.append(course)
        elif course['schedule_day'] == 'M' and course['semester'] == 'Spring' and course['year'] == 2024:
            springm24.append(course)
        elif course['schedule_day'] == 'M' and course['semester'] == 'Summer' and course['year'] == 2022:
            summerm22.append(course)
        elif course['schedule_day'] == 'M' and course['semester'] == 'Summer' and course['year'] == 2023:
            summerm23.append(course)
        elif course['schedule_day'] == 'M' and course['semester'] == 'Summer' and course['year'] == 2024:
            summerm24.append(course)
        elif course['schedule_day'] == 'T' and course['semester'] == 'Fall' and course['year'] == 2022:
            fallt22.append(course)
        elif course['schedule_day'] == 'T' and course['semester'] == 'Fall' and course['year'] == 2023:
            fallt23.append(course)
        elif course['schedule_day'] == 'T' and course['semester'] == 'Fall' and course['year'] == 2024:
            fallt24.append(course)
        elif course['schedule_day'] == 'T' and course['semester'] == 'Spring' and course['year'] == 2022:
            springt22.append(course)
        elif course['schedule_day'] == 'T' and course['semester'] == 'Spring' and course['year'] == 2023:
            springt23.append(course)
        elif course['schedule_day'] == 'T' and course['semester'] == 'Spring' and course['year'] == 2024:
            springt24.append(course)
        elif course['schedule_day'] == 'T' and course['semester'] == 'Summer' and course['year'] == 2022:
            summert22.append(course)
        elif course['schedule_day'] == 'T' and course['semester'] == 'Summer' and course['year'] == 2023:
            summert23.append(course)
        elif course['schedule_day'] == 'T' and course['semester'] == 'Summer' and course['year'] == 2024:
            summert24.append(course)
        elif course['schedule_day'] == 'W' and course['semester'] == 'Fall' and course['year'] == 2022:
            fallw22.append(course)
        elif course['schedule_day'] == 'W' and course['semester'] == 'Fall' and course['year'] == 2023:
            fallw23.append(course)
        elif course['schedule_day'] == 'W' and course['semester'] == 'Fall' and course['year'] == 2024:
            fallw24.append(course)
        elif course['schedule_day'] == 'W' and course['semester'] == 'Spring' and course['year'] == 2022:
            springw22.append(course)
        elif course['schedule_day'] == 'W' and course['semester'] == 'Spring' and course['year'] == 2023:
            springw23.append(course)
        elif course['schedule_day'] == 'W' and course['semester'] == 'Spring' and course['year'] == 2024:
            springw24.append(course)
        elif course['schedule_day'] == 'W' and course['semester'] == 'Summer' and course['year'] == 2022:
            summerw22.append(course)
        elif course['schedule_day'] == 'W' and course['semester'] == 'Summer' and course['year'] == 2023:
            summerw23.append(course)
        elif course['schedule_day'] == 'W' and course['semester'] == 'Summer' and course['year'] == 2024:
            summerw24.append(course)
        elif course['schedule_day'] == 'R' and course['semester'] == 'Fall' and course['year'] == 2022:
            fallr22.append(course)
        elif course['schedule_day'] == 'R' and course['semester'] == 'Fall' and course['year'] == 2023:
            fallr23.append(course)
        elif course['schedule_day'] == 'R' and course['semester'] == 'Fall' and course['year'] == 2024:
            fallr24.append(course)
        elif course['schedule_day'] == 'R' and course['semester'] == 'Spring' and course['year'] == 2022:
            springr22.append(course)
        elif course['schedule_day'] == 'R' and course['semester'] == 'Spring' and course['year'] == 2023:
            springr23.append(course)
        elif course['schedule_day'] == 'R' and course['semester'] == 'Spring' and course['year'] == 2024:
            springr24.append(course)
        elif course['schedule_day'] == 'R' and course['semester'] == 'Summer' and course['year'] == 2022:
            summerr22.append(course)
        elif course['schedule_day'] == 'R' and course['semester'] == 'Summer' and course['year'] == 2023:
            summerr23.append(course)
        elif course['schedule_day'] == 'R' and course['semester'] == 'Summer' and course['year'] == 2024:
            summerr24.append(course)
        elif course['schedule_day'] == 'F' and course['semester'] == 'Fall' and course['year'] == 2022:
            fallf22.append(course)
        elif course['schedule_day'] == 'F' and course['semester'] == 'Fall' and course['year'] == 2023:
            fallf23.append(course)
        elif course['schedule_day'] == 'F' and course['semester'] == 'Fall' and course['year'] == 2024:
            fallf24.append(course)
        elif course['schedule_day'] == 'F' and course['semester'] == 'Spring' and course['year'] == 2022:
            springf22.append(course)
        elif course['schedule_day'] == 'F' and course['semester'] == 'Spring' and course['year'] == 2023:
            springf23.append(course)
        elif course['schedule_day'] == 'F' and course['semester'] == 'Spring' and course['year'] == 2024:
            springf24.append(course)
        elif course['schedule_day'] == 'F' and course['semester'] == 'Summer' and course['year'] == 2022:
            summerf22.append(course)
        elif course['schedule_day'] == 'F' and course['semester'] == 'Summer' and course['year'] == 2023:
            summerf23.append(course)
        elif course['schedule_day'] == 'F' and course['semester'] == 'Summer' and course['year'] == 2024:
            summerf24.append(course)
    for day in [fallm22, fallm23, fallm24, springm22, springm23, springm24, summerm22, summerm23, summerm24, fallt22, fallt23, fallt24, springt22, springt23, springt24, summert22, summert23, summert24, fallw22, fallw23, fallw24, springw22, springw23, springw24, summerw22, summerw23, summerw24, fallr22, fallr23, fallr24, springr22, springr23, springr24, summerr22, summerr23, summerr24, fallf22, fallf23, fallf24, springf22, springf23, springf24, summerf22, summerf23, summerf24]:
        day_times = []
        for course in day:
            start_time = course['start_time']
            end_time = course['end_time']
            day_times.append((start_time, end_time))
        for i, course1 in enumerate(day_times):
            for j, course2 in enumerate(day_times):
                if i != j:
                    if check_overlap(course1, course2):
                        return False
    return True


def get_course_catalog(db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)
    cursor.execute("""SELECT c.department, c.course_num, c.title, c.credit, 
        p.prereq_one_dep, p.prereq_one_num, 
        p.prereq_two_dep, p.prereq_two_num
        FROM course c
        LEFT JOIN prerequisite p ON c.department = p.course_dep AND c.course_num = p.course_num""")
    course_catalog = cursor.fetchall()
    return course_catalog

def admit(user_id: str, db: mysql.connector.MySQLConnection):
    cursor = db.cursor(dictionary=True)

    cursor.execute(f"UPDATE user SET role = 'grad_stu' WHERE user.user_id = '{user_id}'")

    db.commit()

    cursor.execute(f"SELECT * FROM application WHERE application.user_id = '{user_id}'")

    app_data = cursor.fetchone()

    query = "INSERT INTO student (uid, user_id, advisor_id, program, major, gpa, cleared) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    parameters = (app_data['uid'], user_id, 3, app_data['degreessought'], app_data['areas_interest'], '0.0', 0)

    cursor.execute(query, parameters)

    return

def send_email(user_id: str, first_name: str, last_name: str, receiver_name: str, receiver_email: str, special_code_str: str):
    sender_email = "amzgwu@gmail.com"
    password = "yosj bbse rxzq pfna"
    try:
        # Create a MIME object
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Recommendation Letter for " + first_name + " " + last_name

        # Add body to the email
        body = f"Hello " + receiver_name + "\n\nYou have been selected to be a recommender by " + first_name + " " + last_name + ". Please send an email to amzgwu@gmail.com with your recommendation. Include this code in the subject: " + special_code_str + "\n\n\nSincerely,\nAMZ University"
        message.attach(MIMEText(body, "plain"))

        # Initialize SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)

        # Send email
        server.sendmail(sender_email, receiver_email, message.as_string())

        # Close the SMTP server
        server.quit()
    except Exception as e:
        print("An error occurred:", e)

    return

def email_recommenders(user_id: str, first_name: str, last_name: str, rec_name_one: str, rec_email_one: str, rec_name_two: str, rec_email_two: str, rec_name_three: str, rec_email_three: str, db: mysql.connector.MySQLConnection):
    cursor = db.cursor(dictionary=True)
    
    special_code = datetime.now()

    special_code_str = str(special_code)

    query = "UPDATE recommendationletter SET code = %s WHERE recommendationletter.user_id = %s"
    parameter = (special_code_str, user_id)
    cursor.execute(query, parameter)
    db.commit()

    if rec_name_one and rec_email_one:
        send_email(user_id, first_name, last_name, rec_name_one, rec_email_one, special_code_str)
    if rec_name_two and rec_email_two:
        send_email(user_id, first_name, last_name, rec_name_two, rec_email_two, special_code_str)
    if rec_name_three and rec_email_three:
        send_email(user_id, first_name, last_name, rec_name_three, rec_email_three, special_code_str)
    return

def refresh_email(user_id: str, db: mysql.connector.MySQLConnection):

    cursor = db.cursor(dictionary=True)
    sender_email = "amzgwu@gmail.com"
    password = "yosj bbse rxzq pfna"
    imap_server = "imap.gmail.com"
    static_folder = os.path.join(os.getcwd(), 'static')
    filepath = os.path.join(static_folder, 'transcript')

    # Define the list of sender email addresses to filter
    sender_emails = []

    cursor.execute(f"SELECT * from recommendationletter where user_id = '{user_id}'")

    emails = cursor.fetchone()

    special_code = emails['code']

    if emails['rec_email_one']:
        sender_emails.append(emails['rec_email_one'])
    if emails['rec_email_two']:
        sender_emails.append(emails['rec_email_two'])
    if emails['rec_email_three']:
        sender_emails.append(emails['rec_email_three'])

    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(imap_server)

    # Login to the account
    mail.login(sender_email, password)

    # Select the mailbox (inbox in this case)
    mail.select("inbox")

    rec_num = 0

    # Iterate through each sender email
    for sender_email in sender_emails:

        rec_num += 1
        key = 'FROM'
        value = sender_email
        # Search for emails from the specified sender
        status, data = mail.search(None, key, value)

        mail_list = data[0].split()

        messages = []

        # Iterate through each email
        for mail_id in mail_list:
            # Fetch the email
            status, data = mail.fetch(mail_id, "(RFC822)")
            messages.append(data)

        for message in messages[::-1]:
            for response_part in message:
                if type(response_part) is tuple:
                    my_msg = email.message_from_bytes((response_part[1]))
                    subject_ = my_msg['subject']
                    from_ = my_msg['from']
                    body = ""
                    for part in my_msg.walk():
                        if part.get_content_type() == 'text/plain':
                            body += part.get_payload()
                        elif part.get_content_type() == "application/pdf":
                            original_filename = part.get_filename()
                            filename, extension = os.path.splitext(original_filename)
                            filename_with_user_id = filename + str(user_id) + extension
                            file_full_path = os.path.join(filepath, filename_with_user_id)
                            if not os.path.isfile(file_full_path):
                                with open(file_full_path, 'wb') as fp:
                                    fp.write(part.get_payload(decode=True))  
                            save_filename(filename_with_user_id, connect_db())   
                            update_transcript_submission_received(user_id, connect_db())     
                    if special_code in subject_:
                        if rec_num == 1:
                            query = "UPDATE recommendationletter SET rec_letter_one = %s, status_one = 'received' WHERE recommendationletter.user_id = %s"
                            parameter = (body, user_id)
                            cursor.execute(query, parameter)
                        if rec_num == 2:
                            query = "UPDATE recommendationletter SET rec_letter_two = %s, status_two = 'received' WHERE recommendationletter.user_id = %s"
                            parameter = (body, user_id)
                            cursor.execute(query, parameter)
                        if rec_num == 3:
                            query = "UPDATE recommendationletter SET rec_letter_three = %s, status_three = 'received' WHERE recommendationletter.user_id = %s"
                            parameter = (body, user_id)
                            cursor.execute(query, parameter)

        cursor.execute(f"SELECT * FROM user WHERE user.user_id = '{user_id}'")

        user_email = cursor.fetchone()

        user_email_transcript = user_email['email']

        key = 'FROM'
        value = user_email_transcript
        # Search for emails from the specified sender
        status, data = mail.search(None, key, value)

        mail_list = data[0].split()

        messages = []

        # Iterate through each email
        for mail_id in mail_list:
            # Fetch the email
            status, data = mail.fetch(mail_id, "(RFC822)")
            messages.append(data)

        for message in messages[::-1]:
            for response_part in message:
                if type(response_part) is tuple:
                    my_msg = email.message_from_bytes((response_part[1]))
                    subject_ = my_msg['subject']
                    from_ = my_msg['from']
                    body = ""
                    for part in my_msg.walk():
                        if part.get_content_type() == "application/pdf":
                            original_filename = part.get_filename()
                            filename, extension = os.path.splitext(original_filename)
                            filename_with_user_id = filename + str(user_id) + extension
                            file_full_path = os.path.join(filepath, filename_with_user_id)
                            if not os.path.isfile(file_full_path):
                                with open(file_full_path, 'wb') as fp:
                                    fp.write(part.get_payload(decode=True))  
                            save_filename(user_id, filename_with_user_id, connect_db())   
                            update_transcript_submission_received(user_id, connect_db())
    mail.logout()
    db.commit()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_login(
    email: str, password: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """checks the login, then returns all data related to the user
    (user_id, Email, Username, Password, Role)"""

    cursor = db.cursor(dictionary=True)

    checklogin = "SELECT * FROM user WHERE email = %s AND password = %s"
    checkloginvalues = (email, password)

    cursor.execute(checklogin, checkloginvalues)

    userdata = cursor.fetchone()
    if userdata is not None:
        cursor.close()
        return userdata

    return None


def grab_role(user_id, db: mysql.connector.connection.MySQLConnection) -> dict:
    """grabs the role related to the user"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT role FROM user WHERE user_id = '{user_id}'")
    role = cursor.fetchone()

    return role


def check_email(email: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Validates the existence of an email in the database"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT email FROM user WHERE email = '{email}'")
    email = cursor.fetchone()

    return email

def admin_adduser(email:str, username: str, password:str,fname:str,lname:str,address:str,dob:str,role:str,db:mysql.connector.MySQLConnection):

    cursor = db.cursor(dictionary=True)
    adduser = (
        "INSERT INTO user (email, username, password, first_name, last_name, dob, address, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )

    adduservalues = (email, username, password, fname, lname, dob, address, role)

    cursor.execute(adduser, adduservalues)

    return
def add_user(
    first_name: str,
    last_name: str,
    dob_str: str,
    email: str,
    username: str,
    password: str,
    street_address: str,
    city: str,
    state: str,
    postal_code: str,
    db: mysql.connector.connection.MySQLConnection,
    role="user",
) -> bool:
    """Add a user to the USER table in the database"""

    cursor = db.cursor(dictionary=True)

    dob = datetime.strptime(dob_str, '%Y-%m-%d')
    address = f"{street_address}, {city}, {state} {postal_code}"

    adduser = (
        "INSERT INTO user (email, username, password, first_name, last_name, dob, address, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    adduservalues = (email, username, password, first_name, last_name, dob, address, role)

    cursor.execute(adduser, adduservalues)

    return True


def get_advisees(user_id: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM student JOIN user ON student.user_id = user.user_id WHERE student.advisor_id = '{user_id}'")

    list_of_advisees = cursor.fetchall()

    return list_of_advisees

def get_university_id(user_id: str, db: mysql.connector.connection.MySQLConnection) -> str:
    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT uid FROM student WHERE student.user_id = '{user_id}'")

    uid = cursor.fetchone()

    if not uid:
        cursor.execute(f"SELECT university_id FROM alumni WHERE alumni.user_id = '{user_id}'")

        uid = cursor.fetchone()

    return uid

def get_all_students(db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student JOIN user ON student.user_id = user.user_id")

    students = cursor.fetchall()

    return students

def get_all_advisors(db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM user WHERE role = 'fac_adv'")

    advisors = cursor.fetchall()

    return advisors

def get_student_information(uid: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM student JOIN user ON student.user_id = user.user_id WHERE student.uid = %s"
    parameters = (str(uid),)

    cursor.execute(query, parameters)

    student_information = cursor.fetchone()

    if student_information:
        return student_information

    return None

def get_student_information_by_uid(uid: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM student JOIN user ON student.user_id = user.user_id WHERE student.uid = %s"
    parameters = (str(uid),)

    cursor.execute(query, parameters)

    student_information = cursor.fetchall()

    if student_information:
        return student_information

    return None

def get_student_information_by_lname(lname: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM student JOIN user ON student.user_id = user.user_id WHERE user.last_name = %s"
    parameters = (str(lname),)

    cursor.execute(query, parameters)

    student_information = cursor.fetchall()

    if student_information:
        return student_information

    return None

def set_advisor(advisor_id: str, user_id:str, db: mysql.connector.connection.MySQLConnection):
    cursor = db.cursor(dictionary=True)

    cursor.execute("UPDATE student SET advisor_id = %s WHERE user_id = %s", (advisor_id, user_id))

    db.commit()

    return 

def get_alumni_info(uid: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM alumni WHERE university_id = %s", (uid,))

    alumni = cursor.fetchall()

    return alumni

def get_courses_taken(uid: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM course_taken WHERE course_taken.university_id = %s"
    parameters = (str(uid),)

    cursor.execute(query, parameters)
    
    courses_taken = cursor.fetchall()

    return courses_taken
def get_course_schedule(db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM schedule")
    
    course_schedule = cursor.fetchall()

    return course_schedule
def get_form_one(uid: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM forms WHERE forms.submitted_university_id = %s ORDER BY form_id DESC LIMIT 1"
    parameters = (uid,)

    cursor.execute(query, parameters)

    form = cursor.fetchone()

    return form
def get_form_classes(uid: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    form = get_form_one(uid, db)

    if not form:

        return None
    
    query = "SELECT * FROM forms_classes WHERE forms_classes.university_id  = %s"
    parameters = (uid,)

    cursor.execute(query, parameters)

    form_classes = cursor.fetchall()

    return form_classes
def approve_form_one(uid:str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute('UPDATE forms SET approved = 1 WHERE submitted_university_id = %s', (uid,))

    cursor.execute('UPDATE student SET advising_hold = 1 WHERE uid = %s', (uid,))

    db.commit()

    return
def approve_graduation(uid:str, db: mysql.connector.MySQLConnection):
    cursor = db.cursor(dictionary=True)

    cursor.execute('UPDATE graduation_application SET approved = 1 WHERE submitted_university_id = %s', (uid,))

    cursor.execute("UPDATE student SET cleared = 1 WHERE uid = %s", (uid,))

    db.commit()

    return
def get_applicants(db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM user WHERE role = 'applicant'")

    applicants = cursor.fetchall()

    return applicants
def get_assigned_classes(user_id: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM schedule WHERE instructor_id = %s", (user_id,))

    assigned_classes = cursor.fetchall()

    return assigned_classes
def get_students_in_class(crn: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM course_taken JOIN student ON course_taken.university_id = student.uid JOIN user ON student.user_id = user.user_id WHERE crn = %s", (crn,))

    students = cursor.fetchall()

    return students
def get_class(crn: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM schedule WHERE crn = %s", (crn,))

    class_ = cursor.fetchone()

    return class_
def get_app_data(user_id: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Retrieves all application data for the specified user"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"SELECT * FROM application JOIN recommendationletter ON application.user_id = recommendationletter.user_id WHERE application.user_id = '{user_id}'"
    )
    user_data = cursor.fetchone()

    # Send back the user data
    return user_data


def get_app_data_appid(
    applicationid: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Retrieves all application data for the specified application"""
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"SELECT * FROM application JOIN recommendationletter ON application.applicationid = recommendationletter.letterid WHERE application.applicationid = '{applicationid}'"
    )
    user_data = cursor.fetchone()

    # Send back the user data
    return user_data


def get_degrees_appid(applicationid: str) -> tuple:
    """Generates a tuple containing information for the BS and MS in the
    following order (BS_Info, MS_Info)"""

    priordegreeinfo = get_prior_degree_info_appid(applicationid, connect_db())
    priordegreeinfoBS = []
    priordegreeinfoMS = []

    # Check the amount of priordegrees, and pass in all the values to the
    # respective variable (priordegreeinfoBS or priordegreeinfoMS ) i.e. If
    # there are 2 rows in priordegrees, it means they have 2 a BS and a MS
    if len(priordegreeinfo) == 2:
        priordegreeinfoBS = priordegreeinfo[0]
        priordegreeinfoMS = priordegreeinfo[1]
    elif len(priordegreeinfo) == 1:
        priordegreeinfoBS = priordegreeinfo[0]
    else:
        print("No Prior Degrees found")

    # return a tuple containing info for both degrees (BS_Info, MS_Info)
    return priordegreeinfoBS, priordegreeinfoMS


def get_prior_degree_info_appid(
    applicationid: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Fetches the prior_degree info for a given user_id from the database"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"SELECT * FROM priordegrees WHERE applicationid = '{applicationid}'"
    )
    info = cursor.fetchall()

    return info


def get_all_reviews(db: mysql.connector.MySQLConnection) -> dict:
    cursor = db. cursor(dictionary=True)

    cursor.execute("SELECT * FROM reviewform")

    reviews = cursor.fetchall()

    return reviews

def get_all_reviews_by_user_id(user_id: str, db:mysql.connector.MySQLConnection) -> dict:
    cursor = db. cursor(dictionary=True)

    cursor.execute("SELECT * FROM reviewform WHERE user_id = %s", (user_id,))

    reviews = cursor.fetchall()

    return reviews


def get_pending_review_apps(
    user_id: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Retrieves all applications that are pending review"""
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"SELECT * FROM application LEFT JOIN user ON application.user_id = user.user_id LEFT JOIN recommendationletter on application.applicationid = recommendationletter.letterid INNER JOIN transcript ON application.applicationid = transcript.transcriptid WHERE applicationid NOT IN (SELECT reviewid FROM been_reviewed WHERE reviewerid = '{user_id}') AND application.status = 'application complete and under review' AND role = 'applicant' AND transcriptstatus = 'received' ORDER BY timestamp ASC"
    )
    apps = cursor.fetchall()

    return apps

def get_cac_apps(
    user_id: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Retrieves all applications that are pending review"""
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"SELECT * FROM application LEFT JOIN user ON application.user_id = user.user_id LEFT JOIN recommendationletter on application.applicationid = recommendationletter.letterid INNER JOIN transcript ON application.applicationid = transcript.transcriptid WHERE application.status = 'application complete and under review' AND role = 'applicant' AND transcriptstatus = 'received' ORDER BY timestamp ASC"
    )
    apps = cursor.fetchall()

    return apps

def has_reviewed(user_id: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM been_reviewed WHERE reviewerid = '{user_id}'")

    reviewer = cursor.fetchall()

    return reviewer

def num_applications(db: mysql.connector.connection.MySQLConnection) -> str:
    """Checks for the current number of applications. Takes the cursor and
    returns (Number of Applications)"""
    cursor = db.cursor(dictionary=True)
    number = 0

    cursor.execute("SELECT COUNT(applicationid) FROM application")
    number = cursor.fetchone()

    return number[0]


def save_app(
    user_id: str,
    firstname: str,
    lastname: str,
    address: str,
    ssn: str,
    phonenumber: str,
    priordegrees: dict,
    degreessought: str,
    areas_interest: str,
    greverbal: str,
    grequantitative: str,
    priorwork: str,
    greyearofexam: str,
    greadvancedscore: str,
    greadvancedsubject: str,
    semester: str,
    year: str,
    rec_name_one: str,
    rec_email_one: str,
    rec_name_two: str,
    rec_email_two: str,
    rec_name_three: str,
    rec_email_three: str,
    transcript_submission: str
) -> None:
    """Saves all current progress from the application form into the application
    table"""

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # if the prior degree is not specified, then continue with num_degrees = 0
    if priordegrees is not None:
        num_degrees = len(priordegrees.keys())
    else:
        num_degrees = 0

    # 2 degrees implies MS is the highest
    if num_degrees == 2:
        priordegree = "MS"
    # 1 degree implies BS is the highest
    elif num_degrees == 1:
        priordegree = "BS"
    else:
        priordegree = None

    validate = app_exists(user_id, connect_db())["count"]

    # if there are no application entries for the specified user
    if validate == 0:
        """
          ___                  __   _              __    _                    ____         ___    
         / _ |   ___    ___   / /  (_) ____ ___ _ / /_  (_) ___   ___        /  _/  ___   / _/ ___
        / __ |  / _ \  / _ \ / /  / / / __// _ `// __/ / / / _ \ / _ \      _/ /   / _ \ / _/ / _ \
       /_/ |_| / .__/ / .__//_/  /_/  \__/ \_,_/ \__/ /_/  \___//_//_/     /___/  /_//_//_/   \___/
              /_/    /_/                                                                          
        """

        saveinsertapp = """
        INSERT INTO application
        (user_id, status, decision, timestamp, firstname, lastname,
        address, ssn, phonenumber, degreessought, areas_interest, priordegrees,
        greverbal, grequantitative, greyearofexam, greadvancedscore, greadvancedsubject,
        priorwork, semester, year, transcript_submission)
        VALUES
        (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s,
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s)
    """

        saveinsertappvalues = (
            user_id,
            "application incomplete",
            "undecided",
            firstname,
            lastname,
            address,
            ssn,
            phonenumber,
            degreessought,
            areas_interest,
            priordegree,
            greverbal,
            grequantitative,
            greyearofexam,
            greadvancedscore,
            greadvancedsubject,
            priorwork,
            semester,
            year,
            transcript_submission
        )

        cursor.execute(saveinsertapp, saveinsertappvalues)

        """
           ___          _                    ___                                     ____         ___    
          / _ \  ____  (_) ___   ____       / _ \ ___   ___ _  ____ ___  ___        /  _/  ___   / _/ ___
         / ___/ / __/ / / / _ \ / __/      / // // -_) / _ `/ / __// -_)/ -_)      _/ /   / _ \ / _/ / _ \
        /_/    /_/   /_/  \___//_/        /____/ \__/  \_, / /_/   \__/ \__/      /___/  /_//_//_/   \___/
                                                      /___/                                              
        """

        app_id = get_app_id(connect_db(), user_id)

        # loop through prior degrees and add each one to prior degrees table
        for i in range(num_degrees):
            degree_type = list(priordegrees.keys())[i]
            degree_dict = priordegrees[degree_type]
            cursor.execute(
                f"INSERT into priordegrees \
                (applicationid, user_id, degree_type, year, \
                gpa, school, major) \
                VALUES ('{app_id}', '{user_id}', '{degree_type}', '{degree_dict['year']}', \
                '{degree_dict['gpa']}', '{degree_dict['university']}', '{degree_dict['major']}')"
            )

        """
           ___                                              __        __    _                    __        __   __            
          / _ \ ___  ____ ___   __ _   __ _  ___   ___  ___/ / ___ _ / /_  (_) ___   ___        / /  ___  / /_ / /_ ___   ____
         / , _// -_)/ __// _ \ /  ' \ /  ' \/ -_) / _ \/ _  / / _ `// __/ / / / _ \ / _ \      / /__/ -_)/ __// __// -_) / __/
        /_/|_| \__/ \__/ \___//_/_/_//_/_/_/\__/ /_//_/\_,_/  \_,_/ \__/ /_/  \___//_//_/     /____/\__/ \__/ \__/ \__/ /_/  
                                                                                                                     
        """
        cursor.execute(
            f"INSERT into recommendationletter (user_id, rec_name_one, rec_email_one, rec_name_two, rec_email_two, rec_name_three, rec_email_three, status_one, status_two, status_three) VALUES ('{user_id}', '{rec_name_one}', '{rec_email_one}', '{rec_name_two}', '{rec_email_two}', '{rec_name_three}', '{rec_email_three}','not received','not received','not received')"
        )

    else:

        """
          ___                  __   _              __    _                    ____         ___    
         / _ |   ___    ___   / /  (_) ____ ___ _ / /_  (_) ___   ___        /  _/  ___   / _/ ___
        / __ |  / _ \  / _ \ / /  / / / __// _ `// __/ / / / _ \ / _ \      _/ /   / _ \ / _/ / _ \
       /_/ |_| / .__/ / .__//_/  /_/  \__/ \_,_/ \__/ /_/  \___//_//_/     /___/  /_//_//_/   \___/
              /_/    /_/                                                                          
        """

        saveupdateapp = """
        UPDATE application
        SET firstname = %s, lastname = %s, address = %s,
        ssn = %s, phonenumber = %s, degreessought = %s,
        areas_interest = %s, priordegrees = %s,
        greverbal = %s, grequantitative = %s,
        priorwork = %s, semester = %s, year = %s,
        greyearofexam = %s, greadvancedscore = %s,
        greadvancedsubject = %s, transcript_submission = %s
        WHERE user_id = %s
    """

        saveupdateappvalues = (
            firstname,
            lastname,
            address,
            ssn,
            phonenumber,
            degreessought,
            areas_interest,
            priordegree,
            greverbal,
            grequantitative,
            priorwork,
            semester,
            year,
            greyearofexam,
            greadvancedscore,
            greadvancedsubject,
            transcript_submission,
            user_id,
        )

        cursor.execute(saveupdateapp, saveupdateappvalues)

        # Delete previous entries
        cursor.execute(f"DELETE FROM priordegrees WHERE user_id = '{user_id}'")
        # Prior degree info insertion
        app_id = get_app_id(connect_db(), user_id)

        """
           ___          _                    ___                                     ____         ___    
          / _ \  ____  (_) ___   ____       / _ \ ___   ___ _  ____ ___  ___        /  _/  ___   / _/ ___
         / ___/ / __/ / / / _ \ / __/      / // // -_) / _ `/ / __// -_)/ -_)      _/ /   / _ \ / _/ / _ \
        /_/    /_/   /_/  \___//_/        /____/ \__/  \_, / /_/   \__/ \__/      /___/  /_//_//_/   \___/
                                                      /___/                                              
        """

        # loop through prior degrees and add each one to prior degrees table
        for i in range(num_degrees):
            degree_type = list(priordegrees.keys())[i]
            degree_dict = priordegrees[degree_type]

            savepd = """
    INSERT INTO priordegrees
    (applicationid, user_id, degree_type, year, gpa, school, major)
    VALUES
    (%(app_id)s, %(user_id)s, %(degree_type)s, %(year)s, %(gpa)s, %(school)s, %(major)s)
"""

            savepdvalues = {
                "app_id": app_id,
                "user_id": user_id,
                "degree_type": degree_type,
                "year": degree_dict["year"],
                "gpa": degree_dict["gpa"],
                "school": degree_dict["university"],
                "major": degree_dict["major"],
            }

            cursor.execute(savepd, savepdvalues)

        """
           ___                                              __        __    _                    __        __   __            
          / _ \ ___  ____ ___   __ _   __ _  ___   ___  ___/ / ___ _ / /_  (_) ___   ___        / /  ___  / /_ / /_ ___   ____
         / , _// -_)/ __// _ \ /  ' \ /  ' \/ -_) / _ \/ _  / / _ `// __/ / / / _ \ / _ \      / /__/ -_)/ __// __// -_) / __/
        /_/|_| \__/ \__/ \___//_/_/_//_/_/_/\__/ /_//_/\_,_/  \_,_/ \__/ /_/  \___//_//_/     /____/\__/ \__/ \__/ \__/ /_/  
                                                                                                                     
        """

        cursor.execute(
            f"UPDATE recommendationletter SET rec_name_one = '{rec_name_one}', rec_email_one = '{rec_email_one}', rec_name_two = '{rec_name_two}', rec_email_two = '{rec_email_two}', rec_name_three= '{rec_name_three}', rec_email_three = '{rec_email_three}', WHERE user_id = '{user_id}'"
        )

    change_user_role(user_id, "applicant", connect_db())

    cursor.close()

    return

def reset_application(user_id: str, db: mysql.connector.MySQLConnection):
    cursor = db.cursor(dictionary=True)

    cursor.execute("SET foreign_key_checks = 0")

    cursor.execute("DELETE FROM application WHERE user_id = %s", (user_id,))
    db.commit()
    cursor.execute("DELETE FROM recommendationletter WHERE user_id = %s", (user_id,))
    db.commit()
    cursor.execute("DELETE FROM priordegrees WHERE user_id = %s", (user_id,))
    db.commit()

    cursor.execute("SET foreign_key_checks = 1")

    return


def save_filename(user_id: str, filename: str, db: mysql.connector.MySQLConnection):
    cursor = db.cursor(dictionary=True)

    query = "UPDATE application SET transcript_filename = %s WHERE application.user_id = %s"
    parameters = (filename, user_id)

    cursor.execute(query, parameters)

    db.commit()
def get_filename(user_id: str, db: mysql.connector.MySQLConnection):
    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM application WHERE application.user_id = '{user_id}'")

    database_filename = cursor.fetchone()

    filename = database_filename['transcript_filename']

    return filename

def update_transcript_submission_received(user_id: str, db: mysql.connector.MySQLConnection):
    cursor = db.cursor(dictionary=True)

    query = "UPDATE application SET transcript_submission_received = %s WHERE application.user_id = %s"
    parameters = ('received', user_id)

    cursor.execute(query, parameters)

    db.commit()


def submit_app(user_id: str, db: mysql.connector.connection.MySQLConnection) -> None:
    """Submits current application info (Work in Progress)"""

    cursor = db.cursor(dictionary=True)

    uid = generate_uid()
    # Change application status
    cursor.execute(
        f"UPDATE application \
        SET status = 'application complete and under review',\
        timestamp = CURRENT_TIMESTAMP, uid = '{uid}' \
        WHERE user_id = '{user_id}'"
    )

    app_id = get_app_id(connect_db(), user_id)

    transcript_check = validate_transcript(app_id, connect_db())

    print("check:", transcript_check)

    if transcript_check:

        cursor.execute(f"SELECT * FROM transcript WHERE transcript.user_id = '{user_id}'")

        transcript_exists = cursor.fetchone()

        if not transcript_exists:
            cursor.execute(
                f"INSERT INTO transcript (user_id, transcriptstatus) VALUES ('{user_id}', 'not received')"
            )

    return


def submit_review(
    user_id,
    reviewerid,
    rating,
    generic,
    credible,
    gas_decision,
    missing_course,
    reasons_reject,
    reviewer_comment,
    recommended_advisor,
    final_decision,
    db: mysql.connector.connection.MySQLConnection
):

    cursor = db.cursor(dictionary=True)

    reviewid = get_app_id(connect_db(), user_id)

    if not final_decision:
        final_decision = "undecided"
    else:
        cursor.execute(
            f"UPDATE application SET status = 'decision', decision = '{final_decision}' WHERE user_id = '{user_id}'"
        )

    cursor.execute(
        f"INSERT into reviewform (reviewid, user_id, reviewerid, rating, generic, credible, gas_decision, missing_course, reasons_reject, reviewer_comment, recommended_advisor, review_status, finaldecision, timestamp) VALUES ('{reviewid}', '{user_id}', '{reviewerid}', '{rating}', '{generic}', '{credible}', '{gas_decision}', '{missing_course}', '{reasons_reject}', '{reviewer_comment}', '{recommended_advisor}', 'reviewed', '{final_decision}', CURRENT_TIMESTAMP)"
    )

    cursor.execute(
        f"INSERT into been_reviewed (reviewerid, reviewid) VALUES ('{reviewerid}', '{reviewid}')"
    )

    return


def degree_info(num_degree: int, form):
    """Generates a dictionary of information for a specfied users prior degree
    info"""

    if num_degree == 1:
        result = {
            "BS": {
                "year": form.get("yearreceived_bs"),
                "major": form.get("major_bs"),
                "gpa": form.get("gpa_bs"),
                "university": form.get("university_bs"),
            }
        }
    else:
        result = {
            "BS": {
                "year": form.get("yearreceived_bs"),
                "gpa": form.get("gpa_bs"),
                "university": form.get("university_bs"),
                "major": form.get("major_bs"),
            },
            "MS": {
                "year": form.get("yearreceived_ms"),
                "gpa": form.get("gpa_ms"),
                "university": form.get("university_ms"),
                "major": form.get("major_ms"),
            },
        }

    return result


def app_exists(user_id: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Validates the existence of an application in the database for a specified
    user_id"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"SELECT COUNT(applicationid) AS count FROM application WHERE user_id = '{user_id}'"
    )

    result = cursor.fetchone()

    return result


def get_app_status(db: mysql.connector.connection.MySQLConnection, user_id: str) -> str:
    """Fetches the status of an application given a user_id"""
    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT status FROM application WHERE user_id = {user_id}")
    status = cursor.fetchone()

    return status["status"]


def get_app_id(db: mysql.connector.connection.MySQLConnection, user_id: str) -> str:
    """Fetches the applicationid for a given user_id"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT applicationid FROM application WHERE user_id = {user_id}")
    app_id = cursor.fetchone()

    if not app_id:
        return None

    return app_id["applicationid"]


def get_prior_degree_info(
    user_id: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Fetches the prior_degree info for a given user_id from the database"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM priordegrees WHERE user_id = '{user_id}'")
    info = cursor.fetchall()

    return info


def clear_session(session) -> None:
    """Clears all session variables"""

    if "username" in session:
        session.pop("username")
    if "email" in session:
        session.pop("email")
    if "role" in session:
        session.pop("role")
    if "question_history" in session:
        session.pop("question_history")
    if "response_history" in session:
        session.pop("response_history")

    session.clear()

    return


def check_uid(id: int, db: mysql.connector.connection.MySQLConnection) -> bool:
    """Checks to see if a uid exists in the application table"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM application WHERE uid = '{id}'")
    check = cursor.fetchall()

    # If an application entry contains the specified uid, then return true
    if len(check) > 0:
        return True

    return False


def generate_uid() -> int:
    """Generates a unique uid"""

    # The generated uid has not be checked against the application table
    notchecked = True

    while notchecked:

        # Generate an 8 digit number
        uid = random.randint(10000000, 99999999)
        # Check to see if the generated uid exists in the database If not,
        # then break out of the while loop and return the newly generated
        # uid
        if not check_uid(uid, connect_db()):
            notchecked = False

    return uid


def get_uid(user_id: str, db: mysql.connector.MySQLConnection):
    """Retrieves a user's UID given a user_id"""
    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT uid FROM application WHERE user_id = '{user_id}'")

    uid = cursor.fetchone()

    return uid

def get_degrees(user_id: str) -> tuple:
    """Generates a tuple containing information for the BS and MS in the
    following order (BS_Info, MS_Info)"""

    priordegreeinfo = get_prior_degree_info(user_id, connect_db())
    priordegreeinfoBS = []
    priordegreeinfoMS = []

    # Check the amount of priordegrees, and pass in all the values to the
    # respective variable (priordegreeinfoBS or priordegreeinfoMS ) i.e. If
    # there are 2 rows in priordegrees, it means they have 2 a BS and a MS
    if len(priordegreeinfo) == 2:
        priordegreeinfoBS = priordegreeinfo[0]
        priordegreeinfoMS = priordegreeinfo[1]
    elif len(priordegreeinfo) == 1:
        priordegreeinfoBS = priordegreeinfo[0]
    else:
        print("No Prior Degrees found")

    # return a tuple containing info for both degrees (BS_Info, MS_Info)
    return priordegreeinfoBS, priordegreeinfoMS
def username_exists(username: str, db: mysql.connector.MySQLConnection) -> dict:
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM user WHERE user.username = %s", (username,))

    user = cursor.fetchone()

    return user

def get_user_info(user_id: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Get User Info"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM user WHERE user_id = '{user_id}'")
    user_info = cursor.fetchone()

    return user_info


def get_users(db) -> dict:
    """Retrieves all user's and their corresponding information within the user table"""

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()

    return users


def delete_user(user_id: str, role: str, db: mysql.connector.connection.MySQLConnection) -> None:
    """Deletes a user from the database"""

    cursor = db.cursor()
    uid = get_university_id(user_id, db)['uid']
    try:
        if role in ["reviewer", "chair"]:
            # Delete user from the been_reviewed table
            cursor.execute(f"DELETE FROM been_reviewed WHERE reviewerid = '{user_id}'")
            # Delete user from the reviewform table
            cursor.execute(f"DELETE FROM reviewform WHERE reviewerid = '{user_id}'")
        elif role in ["alumni"]:
            cursor.execute(f"DELETE FROM alumni WHERE user_id = '{user_id}'")
        elif role in ["alumni", "grad_stu"]:
            cursor.execute(f"DELETE FROM course_taken WHERE university_id = '{uid}'")
            cursor.execute(f"DELETE FROM forms WHERE submitted_university_id = '{uid}'")
            cursor.execute(f"DELETE FROM forms_classes WHERE university_id = '{uid}'")
            cursor.execute(f"DELETE FROM graduation_application WHERE submitted_university_id = '{uid}'")
            cursor.execute(f"DELETE FROM student WHERE user_id = '{user_id}'")
            cursor.execute(f"DELETE FROM thesis WHERE submitted_university_id = '{uid}'")
        else:
            # Delete user from related tables
            cursor.execute(f"DELETE FROM schedule WHERE instructor_id = '{user_id}'")
            cursor.execute(f"DELETE FROM been_reviewed WHERE reviewid = '{user_id}'")
            cursor.execute(f"DELETE FROM reviewform WHERE user_id = '{user_id}'")
            cursor.execute(f"DELETE FROM recommendationletter WHERE user_id = '{user_id}'")
            cursor.execute(f"DELETE FROM transcript WHERE user_id = '{user_id}'")
            cursor.execute(f"DELETE FROM priordegrees WHERE user_id = '{user_id}'")
            cursor.execute(f"DELETE FROM application WHERE user_id = '{user_id}'")

        # Delete user from the user table
        cursor.execute(f"DELETE FROM user WHERE user_id = '{user_id}'")

        db.commit()
        print("User successfully deleted.")
    except mysql.connector.Error as error:
        db.rollback()
        print("Error:", error)
    finally:
        cursor.close()

    db.commit()


def change_user_role(
    user_id: str, role: str, db: mysql.connector.MySQLConnection
) -> str:
    """Changes the role of a user in the database"""

    cursor = db.cursor(dictionary=True)

    # Change user's role
    cursor.execute(f"UPDATE user SET role = '{role}' WHERE user_id = '{user_id}'")

    db.commit()

    cursor.close()


def get_user_role(user_id: str, db: mysql.connector.connection.MySQLConnection) -> str:
    """Retrieves the specified user's role given a user_id"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT role FROM user WHERE user_id = '{user_id}'")
    role = cursor.fetchone()

    if role:
        return role["role"]

    return None


def update_session_variables(user_id: str, session) -> None:
    """Updates all session variables using current data"""

    user_data = get_user_info(user_id, connect_db())

    session["user_id"] = user_data["user_id"]
    session["username"] = user_data["username"]
    session["email"] = user_data["email"]
    session["role"] = user_data["role"]

    return


def get_rec_info(user_id: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Retrieves all information from the recommendationletter table given a user_id"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM recommendationletter WHERE user_id = '{user_id}'")
    info = cursor.fetchone()

    return info


def validate_review(
    app_id: str, db: mysql.connector.connection.MySQLConnection
) -> bool:
    """Checks to see if a review with the given application id exists in the database
    True means no reviews, False means there exists reviews"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM reviewform WHERE reviewid = '{app_id}'")
    info = cursor.fetchall()

    if len(info) == 0:
        return True
    else:
        return False


def validate_review_reviewer(reviewid, reviewerid, db) -> bool:
    """Checks to see if a review with the given application id and reviewer id exists in the database
    True means yes reviews, False means no reviews"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT reviewid, reviewerid FROM reviewform WHERE reviewid = '{reviewid}' AND reviewerid = '{reviewerid}'"
    )
    result = cursor.fetchall()

    if len(result) > 0:
        return True
    else:
        return False


def validate_transcript(
    app_id: str, db: mysql.connector.connection.MySQLConnection
) -> bool:
    """Checks to see if a transcript with the given application id exists in tshe database
    if True, then there are no transcript, if False, then transcripts exist"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM transcript WHERE transcriptid = '{app_id}'")
    info = cursor.fetchall()

    if len(info) == 0:
        return True
    else:
        return False
    
def get_all_full_applications(db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Retreives all data associated with an application (application, transcript, recommendation, review form) as a dict"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM application LEFT JOIN transcript ON application.applicationid = transcript.transcriptid LEFT JOIN recommendationletter ON application.applicationid = recommendationletter.letterid"
    )
    info = cursor.fetchall()

    return info
def get_full_application_by_uid(
    uid: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Retreives all data associated with an application (application, transcript, recommendation, review form) as a dict"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM application LEFT JOIN transcript ON application.applicationid = transcript.transcriptid LEFT JOIN recommendationletter ON application.applicationid = recommendationletter.letterid WHERE application.uid = '{uid}'"
    )
    info = cursor.fetchall()

    return info

def to_alumni(uid: str, db: mysql.connector.connection.MySQLConnection):
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student WHERE uid = %s", (uid,))

    student = cursor.fetchall()

    current_year = datetime.now().year

    cursor.execute("INSERT INTO alumni (university_id, user_id, year_of_graduation, program, major, gpa) VALUES (%s, %s, %s, %s, %s, %s)", (uid, student[0]['user_id'], current_year, student[0]['program'], student[0]['major'], student[0]['gpa']))


    cursor.execute("UPDATE user SET role = 'alumni' WHERE user_id = %s", (student[0]['user_id'],)   )

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

    cursor.execute("DELETE FROM student WHERE uid = %s", (uid,))

    db.commit()
    return


def get_full_application_by_lname(
    lname: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Retreives all data associated with an application (application, transcript, recommendation, review form) as a dict"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM application LEFT JOIN transcript ON application.applicationid = transcript.transcriptid LEFT JOIN recommendationletter ON application.applicationid = recommendationletter.letterid WHERE application.lastname = '{lname}'"
    )
    info = cursor.fetchall()

    return info

def get_review_info(
    app_id: str, db: mysql.connector.connection.MySQLConnection
) -> dict:
    """Retreives all data associated with an application (application, transcript, recommendation, review form) as a dict"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM application LEFT JOIN transcript ON application.applicationid = transcript.transcriptid LEFT JOIN recommendationletter ON application.applicationid = recommendationletter.letterid INNER JOIN reviewform ON application.applicationid = reviewform.reviewid WHERE application.applicationid = '{app_id}'"
    )
    info = cursor.fetchone()

    return info


def get_review_for_reviewer(app_id: str, reviewerid, db: mysql.connector.MySQLConnection):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM application LEFT JOIN transcript ON application.applicationid = transcript.transcriptid LEFT JOIN recommendationletter ON application.applicationid = recommendationletter.letterid INNER JOIN reviewform ON application.applicationid = reviewform.reviewid WHERE applicationid = '{app_id}' and reviewerid = '{reviewerid}'"
    )
    info = cursor.fetchone()

    return info


def get_reviewer_id(user_id: str, db) -> str:

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT reviewerid FROM reviewform WHERE user_id = '{user_id}'")
    result = cursor.fetchone()

    return result["reviewerid"]


def get_review_status(
    app_id: str, db: mysql.connector.connection.MySQLConnection
) -> str:
    """Retrievews the status of a particular review given a user_id"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT review_status FROM reviewform WHERE reviewid = '{app_id}'")
    status = cursor.fetchone()

    if not status or len(status) == 0:
        return "not reviewed"

    return status["review_status"]


def get_all_reviewed_info(db: mysql.connector.connection.MySQLConnection) -> dict:
    """Returns the info for all reviewed applications"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM application JOIN transcript ON application.user_id = transcript.user_id JOIN recommendationletter ON transcript.user_id = recommendationletter.user_id JOIN reviewform ON application.applicationid = reviewform.reviewid WHERE review_status = 'reviewed'"
    )
    info = cursor.fetchall()

    return info


def get_pending_review_form(db: mysql.connector.connection.MySQLConnection) -> dict:
    """This returns the review form info for undecided applications"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM reviewform INNER JOIN application ON finaldecision = decision and reviewid = applicationid LEFT JOIN transcript ON transcript.transcriptid = applicationid LEFT JOIN recommendationletter ON applicationid = letterid WHERE finaldecision = 'undecided' AND review_status = 'reviewed' AND transcriptstatus = 'received' AND recommendationletter.all_received = 'received'"
    )
    info = cursor.fetchall()

    return info


def set_transcript_status(
    status: str, user_id: str, db: mysql.connector.connection.MySQLConnection
) -> None:
    """Sets the transcript status for the given users application"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"UPDATE transcript SET transcriptstatus = '{status}' WHERE user_id = '{user_id}'"
    )

    return


def get_transcript_status(
    user_id: str, db: mysql.connector.connection.MySQLConnection
) -> str:
    """Retreives the transcript status for the given user's application"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT transcriptstatus FROM transcript WHERE user_id = '{user_id}'")
    status = cursor.fetchone()

    if not status:
        return "not received"

    return status["transcriptstatus"]


def set_final_decision(
    decision: str, app_id: str, db: mysql.connector.connection.MySQLConnection
) -> None:
    """Sets the final decision for the given user's application"""

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        f"UPDATE application SET decision = '{decision}', status = 'decision' WHERE applicationid = '{app_id}'"
    )

    cursor.execute(
        f"UPDATE reviewform SET finaldecision = '{decision}' WHERE reviewid = '{app_id}'"
    )

    return


def get_transcript_info(db: mysql.connector.connection.MySQLConnection) -> list:
    """Get all transcript data that is not received, needs to be updated before reviewform can be submitted"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"SELECT application.user_id, firstname, lastname, transcriptstatus FROM application JOIN transcript ON application.user_id = transcript.user_id WHERE transcriptstatus = 'not received'"
    )
    info = cursor.fetchall()

    return info


def delete_reviewform(
    reviewerid: str, reviewid: str, db: mysql.connector.connection.MySQLConnection
) -> None:
    """Deletes the reviewform corresponding to the given reviewerid and reviewid"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        f"DELETE FROM been_reviewed WHERE (reviewerid = '{reviewerid}') AND (reviewid = '{reviewid}')"
    )
    cursor.execute(
        f"DELETE FROM reviewform WHERE (reviewerid = '{reviewerid}') AND (reviewid = '{reviewid}')"
    )

    return


def get_decision(user_id: str, db: mysql.connector.connection.MySQLConnection) -> str:
    """Retrieves the application decision for the given user's application"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT decision FROM application WHERE user_id = '{user_id}'")
    decision = cursor.fetchone()

    return decision["decision"]


def get_rec_status(user_id: str, db: mysql.connector.connection.MySQLConnection) -> dict:
    """Retrieves the recommendation letter status for the given user's application"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM recommendationletter WHERE user_id = '{user_id}'")
    status = cursor.fetchone()

    return status

def get_history(db: mysql.connector.connection.MySQLConnection) -> dict:
    """Retrieves all the decided applications"""

    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * from application WHERE status = 'decision'")
    history = cursor.fetchall()

    return history


def reset_database() -> None:
    """Clears all info in all tables, and inserts default accounts/dummy data"""

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

    cursor.execute(" DELETE FROM user; ")
    cursor.execute(" ALTER TABLE user AUTO_INCREMENT = 1 ")

    cursor.execute("DELETE FROM application;")
    cursor.execute("ALTER TABLE application AUTO_INCREMENT = 1;")

    cursor.execute(" DELETE FROM priordegrees;")

    cursor.execute(" DELETE FROM transcript;")
    cursor.execute(" ALTER TABLE transcript AUTO_INCREMENT = 1 ")

    cursor.execute(" DELETE FROM recommendationletter;")
    cursor.execute(" ALTER TABLE recommendationletter AUTO_INCREMENT = 1 ")

    cursor.execute(" DELETE FROM reviewform;")
    cursor.execute(" ALTER TABLE reviewform AUTO_INCREMENT = 1 ")

    cursor.execute(" DELETE FROM been_reviewed; ")

    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    # Start State

    cursor.execute(
        " INSERT INTO user ( email, username, password, role) VALUES ('gs@gmail.com', 'gs', 'pass', 'gs'); "
    )
    cursor.execute(
        " INSERT INTO user ( email, username, password, role) VALUES ('chair@gmail.com', 'chair', 'pass', 'chair'); "
    )
    cursor.execute(
        " INSERT INTO user ( email, username, password, role) VALUES ('narahari@gmail.com', 'Bhagirath', 'pass', 'reviewer'); "
    )
    cursor.execute(
        " INSERT INTO user ( email, username, password, role) VALUES ('wood@gmail.com', 'Tim', 'pass', 'reviewer'); "
    )
    cursor.execute(
        " INSERT INTO user ( email, username, password, role) VALUES ('heller@gmail.com', 'Rachelle', 'pass', 'reviewer'); "
    )
    cursor.execute(
        " INSERT INTO user ( email, username, password, role) VALUES ('admin@gmail.com', 'sysadmin', 'pass', 'admin'); "
    )

    # John Lennon

    cursor.execute(
        "INSERT INTO user ( user_id, email, username, password, role) VALUES (7, 'johnlennon@gmail.com', 'johnlennon', 'pass', 'applicant');"
    )
    cursor.execute(
        "INSERT INTO application (applicationid, user_id, status, decision, timestamp, firstname, lastname, address, ssn, phonenumber, degreessought, areas_interest, priordegrees, greverbal, grequantitative, greyearofexam, greadvancedscore, greadvancedsubject, priorwork, uid, semester, year) VALUES (1, 7, 'application complete and under review', 'undecided', CURRENT_TIMESTAMP, 'John', 'Lennon', '123 Main St, City, Country', '111-11-1111', '555-123-4567', 'MS', 'Computer Science', 'BS', '160', '165', '2022', '115', 'Math','Software Engineer', 12312312, 'Fall', '2025')"
    )
    cursor.execute(
        "INSERT INTO priordegrees (applicationid, user_id, degree_type, year, gpa, school, major)VALUES (1, 7, 'BS', '2018', '3.80', 'George Washington University', 'Computer Science')"
    )
    cursor.execute(
        "INSERT INTO recommendationletter (letterid, user_id, rec_name, rec_email, rec_letter, status)VALUES (1, 7, 'Yoko Ono', 'yoko@example.com', 'Strongly recommend John for the program', 'received')"
    )
    cursor.execute(
        "INSERT INTO transcript (user_id, transcriptstatus) VALUES (7, 'received')"
    )

    # Ringo Starr
    cursor.execute(
        "INSERT INTO user ( user_id, email, username, password, role) VALUES (8, 'ringostarr@gmail.com', 'ringostarr', 'pass', 'applicant');"
    )
    cursor.execute(
        "INSERT INTO application (user_id, status, decision, applicationid,firstname, lastname, address, ssn, phonenumber, degreessought, areas_interest, greverbal, grequantitative, greyearofexam, priorwork, uid, semester, year) VALUES (8, 'application incomplete', 'undecided', 2,'Ringo', 'Starr', '456 Oak St, Town, Country', '222-11-1111', '555-987-6543', 'PHD', 'Physics', '155', '160', '2023', 'Research Assistant', 66666666,'Spring', '2025');"
    )
    cursor.execute(
        "INSERT INTO priordegrees (applicationid, user_id, degree_type, year, gpa, school, major) VALUES (2,8, 'BS', '2017', '3.6', 'ABC University', 'Physics');"
    )
    cursor.execute(
        "INSERT INTO recommendationletter (letterid, user_id, rec_name, rec_email, status) VALUES (2, 8, 'Dr. Smith', 'smith@example.com', 'not received');"
    )
    cursor.execute(
        "INSERT INTO transcript (user_id, transcriptstatus) VALUES (8, 'not received')"
    )

    return

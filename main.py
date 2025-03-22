from flask import Flask, flash, session, render_template, redirect, url_for, request, jsonify
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import PyPDF2
import re
from datetime import datetime
import os
from database import (
    connect_db
)
from functions import (
    check_login,
    application_stats,
    get_all_reviews,
    set_advisor,
    get_alumni_info,
    to_alumni,
    add_course,
    admin_adduser,
    check_form_one,
    get_all_students_by_instructor,
    get_all_courses,
    filter_application_semester,
    filter_application_year,
    filter_application_program,
    remove_course_crn,
    filter_students_semester,
    filter_students_year,
    filter_students_program,
    get_all_reviews_by_user_id,
    get_required_courses,
    get_student_information_by_uid,
    filter_students_cleared_graduate,
    get_all_students,
    get_all_advisors,
    get_requirements,
    username_exists,
    get_students_in_class,
    get_assigned_classes,
    get_student_by_instructor,
    get_full_application_by_lname,
    get_student_information_by_lname,
    get_full_application_by_uid,
    get_all_full_applications,
    update_grade,
    get_thesis,
    get_applicants,
    get_filtered_course_schedule,
    approve_form_one,
    get_graduation_application,
    graduation_application_audit,
    course_reg_to_course,
    get_course_schedule,
    phd_registration_check,
    reset_application,
    get_class,
    get_form_one,
    admit,
    update_transcript_submission_received,
    email_recommenders,
    refresh_email,
    allowed_file,
    get_filename,
    get_course_catalog,
    connect_db,
    save_app,
    degree_info,
    check_email,
    add_user,
    get_advisees,
    get_courses_taken,
    get_form_classes,
    get_student_information,
    get_university_id,
    get_app_data,
    save_filename,
    submit_app,
    clear_session,
    get_prior_degree_info,
    get_app_status,
    get_pending_review_apps,
    get_degrees,
    get_user_info,
    reset_database,
    get_users,
    change_user_role,
    delete_user,
    grab_role,
    get_rec_info,
    submit_review,
    get_app_data_appid,
    get_degrees_appid,
    get_all_reviewed_info,
    get_review_info,
    set_transcript_status,
    set_final_decision,
    delete_reviewform,
    get_pending_review_form,
    get_decision,
    get_transcript_status,
    get_rec_status,
    get_app_id,
    get_review_status,
    get_instructors,
    approve_graduation,
    get_history,
    get_uid,
    get_user_role,
    get_prior_degree_info_appid,
    get_review_for_reviewer,
    has_reviewed
)

app = Flask("app")
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = '/static/transcript'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Page On Load, Login Page : from here one can login or register for a new account
@app.route("/", methods=["GET", "POST"])
def login():
    """Routes you based on signup or login, if signup go to the signup template, if login, the session variables are initialized and routed to the roles homepage"""
    if request.method == "POST":

        if "Signup" in request.form:

            return render_template("signup.html")

        if "Login" in request.form:

            email = request.form.get("Email")
            password = request.form.get("Password")

            if not all([email, password]):
                flash("Please fill in all required fields!", "Failed")
                return render_template("login.html")

            user = check_login(email, password, connect_db())

            if user is None:
                flash("Authencation Failed! ", "Failed")
                return render_template("login.html")

            # Initialize Session Variables

            if "user_id" not in session:
                session["user_id"] = user["user_id"]

            if "first_name" not in session:
                session["first_name"] = user["first_name"]

            if "last_name" not in session:
                session["last_name"] = user["last_name"]

            if "dob" not in session:
                session["dob"] = user["dob"]

            if "email" not in session:
                session["email"] = user["email"]

            if "username" not in session:
                session["username"] = user["username"]

            if "address" not in session:
                session["address"] = user["address"]

            if "role" not in session:
                session["role"] = user["role"]
            # Redirect to the right home based on the role

            return roleportal()

    clear_session(session)

    return render_template("login.html")

# For Everyone, Used to return to the original home page for a role
@app.route("/roleportal", methods=["GET", "POST"])
def roleportal():
    """Redirect to the proper home page depending on role"""

    user_id = session["user_id"]
    userrolerow = grab_role(user_id, connect_db())
    userrole = userrolerow["role"]

    if userrole == "applicant":

        return redirect(url_for("applicanthome"))

    if userrole == "admin":

        return redirect(url_for("adminhome"))

    if userrole == "reviewer":

        return redirect(url_for("reviewhome"))

    if userrole == "user":

        return redirect(url_for("userhome"))

    if userrole == "cac":

        return redirect(url_for("cachome"))

    if userrole == "grad_sec":

        return redirect(url_for("gschome"))
    
    if userrole == "grad_stu":

        return redirect(url_for("student_dashboard"))
    
    if userrole == "instructor":

        return redirect(url_for("instructor_dashboard"))
    if userrole == "alumni":
        return redirect(url_for("alumni_dashboard"))
    if userrole == "fac_adv":
        return redirect(url_for("advisor_dashboard"))
    if userrole == 'registrar':
        return redirect(url_for("reghome"))

    # Allows prospective users to create an account in the system
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Gets new registration formation, checks, then generates the new account information in the databasereg
    isitration"""

    if request.method == "POST":
        
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        dob_str = request.form.get("dob")
        email = request.form.get("email")
        username = request.form.get("username").capitalize()
        password = request.form.get("password")
        street_address = request.form.get("street_address")
        city = request.form.get("city")
        state = request.form.get("state")
        postal_code = request.form.get("postal_code")

        if not all([first_name, last_name, dob_str, email, username, password, street_address, city, state, postal_code]):
            flash("Please fill in all required fields!", "Failed")
            return render_template("signup.html")

        if check_email(email, connect_db()) is not None:

            flash("Email already exists!", "Failed")

            return render_template("signup.html")
        else:

            new_user = add_user(first_name, last_name, dob_str, email, username, password, street_address, city, state, postal_code, connect_db())

            if new_user:
                flash("Signup successful! Please login.", "Success")
                return render_template("login.html")
            else:
                flash("Signup failed. Please try again.", "Faied")
                return render_template("signup.html")

    return render_template("signup.html")


# Brings a user to their homepage depending on their role
@app.route("/home", methods=["GET", "POST"])
def home():
    """Brings the user the the correct home page based on
    the role saved within the session variable"""
    if "role" not in session:
        return render_template("login.html")

    role = session["role"]
    if role == "admin":
        return render_template("adminhome.html")
    elif role == "reviewer":
        return render_template("reviewhome.html")
    elif role == "instructor":
        return render_template("instructor_dashboard.html")
    elif role == "grad_stu":
        return render_template("student_dashboard.html")
    elif role == "alummi":
        return render_template("alumni_dashboard.html")
    elif role == "fac_adv":
        return render_template("advisor_dashboard.html")
    else:
        return render_template("applicanthome.html")
# Form One for Registration
@app.route("/form_one", methods = ['GET','POST'])
def form_one():
    message = None
    user_id = session['user_id']
    program = get_student_information(get_university_id(user_id, connect_db())['uid'], connect_db())['program']
    course_catalog = (get_course_catalog(connect_db()))
    required_courses = get_required_courses(program, connect_db())
    requirements = get_requirements(program, connect_db())
    if request.method == 'POST':
        form_one = []
        for course in course_catalog:
            course_name = "select_" + str(course['department']) + "" + str(course['course_num'])
            course_form_name = request.form.get(course_name)
            if course_form_name:
                form_one.append(course)
        if not form_one:
            message = f"Please do not submit an empty form!"
            return render_template("form_one.html", course_catalog = course_catalog, program = program, message = message, required_courses=required_courses, requirements=requirements)
        validation = check_form_one(form_one, program, connect_db())
        if not validation == 'valid':
            message = validation
            return render_template("form_one.html", course_catalog = course_catalog, program = program, message = message, required_courses=required_courses, requirements=requirements)
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO forms (submitted_university_id) VALUES (%s)", (get_university_id(user_id, connect_db())['uid'],))
        db.commit()
        cursor.execute("SELECT form_id FROM forms WHERE forms.submitted_university_id = (%s) ORDER BY form_id DESC LIMIT 1", (get_university_id(user_id, connect_db())['uid'],))
        form_id = cursor.fetchone()[0]
        for course in form_one:
            cursor.execute("INSERT INTO forms_classes (form_id, university_id, dept, course_num, credits) VALUES (%s, %s, %s, %s, %s)", (form_id, get_university_id(user_id, connect_db())['uid'], course['department'], course['course_num'], course['credit']))
            db.commit()
        if program == 'PhD':
            thesis = request.form['large-text']
            cursor.execute("INSERT INTO thesis (form_id, thesis, submitted_university_id) VALUES (%s, %s, %s)", (form_id, thesis, get_university_id(user_id, connect_db())['uid']))
            db.commit()
        message = f"You have successfully submitted your form 1!"
    return render_template("form_one.html", course_catalog = course_catalog, program = program, message = message, required_courses=required_courses, requirements=requirements)
# Register for Classes
@app.route("/register_for_classes", methods=['GET','POST'])
def register_for_classes():
    message = None
    uid = get_university_id(session['user_id'], connect_db())['uid']
    student_information = get_student_information(uid, connect_db())
    if student_information['advising_hold'] == 0:
        return redirect(url_for("student_dashboard", message = "You have an advising hold!"))
    course_schedule = get_course_schedule(connect_db())
    course_catalog = (get_course_catalog(connect_db()))
    form_classes = get_form_classes(uid, connect_db())
    search_query = request.args.get('search')
    if search_query:
       course_schedule = get_filtered_course_schedule(search_query, connect_db())
    if request.method == 'POST':
        if request.form.get('filter_check'):
            filtered_array = request.args.get("filteredArray")
            print(filtered_array)
        else:
            course_schedule_registration = []
            for course in course_schedule:
                course_name = "select_" + str(course['course_dept']) + "" + str(course['course_num']) + "" + str(course['crn'])
                course_registration_name = request.form.get(course_name)
                if course_registration_name:
                    course_schedule_registration.append(course)
            if not course_schedule_registration:
                message = f"Please do not submit an empty registration!"
                return render_template("register_for_classes.html", course_schedule = course_schedule, course_catalog = course_catalog, message = message, form_classes=form_classes)
            # if not overlap_check(course_schedule_registration):
            #     message = "You have overlapping classes"
            #     return render_template("register_for_classes.html", course_schedule = course_schedule, course_catalog = course_catalog, message = message, form_classes=form_classes)
            if student_information['program'] == 'PhD':
                if not phd_registration_check(course_schedule_registration):
                    message = 'You can only register for 6000s classes'
                    return render_template("register_for_classes.html", course_schedule = course_schedule, course_catalog = course_catalog, message = message, form_classes=form_classes)
            db = connect_db()
            cursor = db.cursor()
            for course in course_schedule_registration:
                course_info = course_reg_to_course(course['course_dept'],course['course_num'], connect_db())
                cursor.execute("INSERT INTO course_taken (university_id, dept, course_num, course_title, credits, semester_taken, year, crn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (uid, course_info['department'], course_info['course_num'], course_info['title'], course_info['credit'], course['semester'], course['year'], course['crn']))
                db.commit()
            message = f"You have successfully registered for classes!"
    return render_template("register_for_classes.html", course_schedule = course_schedule, course_catalog = course_catalog, message = message, form_classes=form_classes)
# Student Dashboard
@app.route("/student_dashboard", methods=['GET','POST'])
def student_dashboard():
    message = None
    thesis = None
    if request.args.get('message'):
       message = request.args.get('message')

    uid = get_university_id(session['user_id'], connect_db())['uid']

    student_information = get_student_information(uid, connect_db())

    courses_taken = get_courses_taken(uid, connect_db())
    form_one = get_form_one(uid, connect_db())
    form_classes = get_form_classes(uid, connect_db())

    if student_information['program'] == 'PhD':
        thesis = get_thesis(uid, connect_db())

    graduation_application = get_graduation_application(uid, connect_db())
        
    if request.method == 'POST':
        if request.form.get('Process'):
            drop_courses = []
            for course in courses_taken:
                course_name = "select_" + str(course['dept']) + "" + str(course['course_num']) + "" + str(course['crn'])
                drop = request.form.get(course_name)
                if drop:
                    drop_courses.append(course)
            db = connect_db()
            cursor = db.cursor()
            for course in drop_courses:
                cursor.execute("DELETE FROM course_taken WHERE course_taken.dept = %s AND course_taken.course_num = %s AND course_taken.crn = %s AND university_id = %s", (course['dept'], course['course_num'], course['crn'], uid))
                db.commit()
            message = f"You have dropped the selected courses!"
            return render_template("student_dashboard.html", student_information = student_information, courses_taken = courses_taken, form_classes = form_classes, form_one = form_one, graduation_application = graduation_application, thesis = thesis, message = message)
        if request.form.get('graduation'):
            if not form_one:
                message = "You have not submitted a Form 1!"
                return render_template("student_dashboard.html", student_information = student_information, courses_taken = courses_taken, form_classes = form_classes, form_one = form_one, graduation_application = graduation_application, thesis = thesis, message = message)
            if not form_one['approved']:
                message = "Your Form 1 is not approved!"
                return render_template("student_dashboard.html", student_information = student_information, courses_taken = courses_taken, form_classes = form_classes, form_one = form_one, graduation_application = graduation_application, thesis = thesis, message = message)
            if not courses_taken:
                message = "You have not taken any courses!"
                return render_template("student_dashboard.html", student_information = student_information, courses_taken = courses_taken, form_classes = form_classes, form_one = form_one, graduation_application = graduation_application, thesis = thesis, message = message)
            audit = graduation_application_audit(student_information, courses_taken, connect_db())
            if not audit == "Pass":
                message = audit
            else:
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("INSERT INTO graduation_application (submitted_university_id) VALUES (%s)", (uid,))
                db.commit()
                message = "You have successfully submitted your graduation application!"
        if request.form.get('to_alumni'):
            print("ALUMNI")
            to_alumni(uid, connect_db())
    return render_template("student_dashboard.html", student_information = student_information, courses_taken = courses_taken, form_classes = form_classes, form_one = form_one, graduation_application = graduation_application, thesis = thesis, message = message)


@app.route("/view_classes", methods=['GET','POST'])
def view_classes():
    user_id = session['user_id']
    
    assigned_classes = get_assigned_classes(user_id, connect_db())


    return render_template("view_classes.html", assigned_classes = assigned_classes)

@app.route("/instructor_dashboard", methods=['GET','POST'])
def instructor_dashboard():
    specific_student = None
    user_id = session['user_id']
    user_info = get_user_info(user_id, connect_db()) 
    assigned_classes = get_assigned_classes(user_id, connect_db())

    all_students = get_all_students_by_instructor(user_id, connect_db())

    search_query = request.args.get('search')
    if search_query:
        specific_student = get_student_by_instructor(user_id, search_query, connect_db())
    if request.method == 'POST':
        if request.form.get('selected_course_crn'):
            crn = request.form.get('selected_course_crn')
            students = get_students_in_class(crn, connect_db())
            course = get_class(crn, connect_db())
            return render_template("instructor_dashboard.html", user_info = user_info, assigned_classes = assigned_classes, students = students, course = course)
        if request.form.get('student_uid'):
            student_uid = request.form.get('student_uid')
            new_grade = request.form.get('new_grade')
            crn = request.form.get('course_crn')
            update_grade(student_uid, new_grade, crn, connect_db())
            return render_template("instructor_dashboard.html", user_info = user_info, assigned_classes = assigned_classes)
    return render_template("instructor_dashboard.html", user_info = user_info, assigned_classes = assigned_classes, specific_student = specific_student, search_query =search_query, all_students = all_students)

@app.route("/view_applicants", methods=['GET','POST'])
def view_applicants():
    user_info = get_user_info(session['user_id'], connect_db()) 
    
    applicants = get_applicants(connect_db())

    return render_template("view_applicants.html", user_info = user_info, applicants = applicants)

@app.route("/advisor_dashboard", methods=['GET','POST'])
def advisor_dashboard():
    message = None
    thesis = None
    user_info = get_user_info(session['user_id'], connect_db())

    list_of_advisees = get_advisees(session['user_id'], connect_db())

    if request.method == 'POST':

        if request.form.get('selected_advisee_uid'):
            advisee_uid = request.form.get('selected_advisee_uid')

            advisee_information = get_student_information(advisee_uid, connect_db())

            courses_taken = get_courses_taken(advisee_uid, connect_db())
            
            form_one = get_form_one(advisee_uid, connect_db())

            forms_classes = get_form_classes(advisee_uid, connect_db())

            if advisee_information['program'] == 'PhD':
                thesis = get_thesis(advisee_uid, connect_db())

            graduation_application = get_graduation_application(advisee_uid, connect_db())
            
            return render_template("advisor_dashboard.html", user_info = user_info, advisees = list_of_advisees, advisee_information = advisee_information, courses_taken = courses_taken, form_one = form_one, forms_classes = forms_classes, graduation_application = graduation_application, advisee_uid = advisee_uid, thesis = thesis)
        if request.form.get('approve'):
            advisee_uid = request.args.get('advisee_uid')

            advisee_information = get_student_information(advisee_uid, connect_db())

            courses_taken = get_courses_taken(advisee_uid, connect_db())
            
            form_one = get_form_one(advisee_uid, connect_db())

            forms_classes = get_form_classes(advisee_uid, connect_db())

            if advisee_information['program'] == 'PhD':
                thesis = get_thesis(advisee_uid, connect_db())

            graduation_application = get_graduation_application(advisee_uid, connect_db())

            approve_form_one(advisee_uid, connect_db())

            return render_template("advisor_dashboard.html", user_info = user_info, advisees = list_of_advisees, advisee_information = advisee_information, courses_taken = courses_taken, form_one = form_one, forms_classes = forms_classes, graduation_application = graduation_application, advisee_uid = advisee_uid, thesis = thesis)

    return render_template("advisor_dashboard.html", user_info = user_info, advisees = list_of_advisees)

@app.route("/alumni_dashboard", methods=['GET','POST'])
def alumni_dashboard():
    user_id = session['user_id']
    uid = get_university_id(user_id, connect_db())['university_id']
    user_info = get_user_info(user_id, connect_db())
    alumni_info = get_alumni_info(uid, connect_db())

    courses_taken = get_courses_taken(uid, connect_db())
    form_one = get_form_one(uid, connect_db())
    forms_classes = get_form_classes(uid, connect_db())
    thesis = get_thesis(uid, connect_db())
    




    return render_template("alumni_dashboard.html", user_info = user_info, alumni_info = alumni_info,courses_taken=courses_taken,form_one=form_one,forms_classes=forms_classes,thesis=thesis)


@app.route("/profile", methods=['GET','POST'])
def profile():
    message = None
    user_id = session['user_id']
    user_info = get_user_info(user_id, connect_db())
    
    if request.method == 'POST':
        print("LOST")
        db = connect_db()
        cursor = db.cursor()
        if request.form['email']:
            email = request.form['email']
            cursor.execute("UPDATE user SET email = %s WHERE user_id = %s", (email, user_id))
            db.commit()
        if request.form['username']:
            username = request.form['username']
            if username_exists(username, connect_db()):
                message = f"Username is already exist. Try again"
                return render_template("profile.html", user_info = user_info, message = message)
            cursor.execute("UPDATE user SET username = %s WHERE user_id = %s", (username, user_id))
            db.commit()
            print("LOL")
        if request.form['address']:
            address = request.form['address']
            cursor.execute("UPDATE user SET address = %s WHERE user_id = %s", (address, user_id))
            db.commit()
    return render_template("profile.html", user_info = user_info, message = message)
# A section which allows the user to enter, save, correct, and submit
# all needed information for the application process.
@app.route("/application", methods=["GET", "POST"])
def application():
    """
    Returns:

    Returns template for application with user application data Retrieves
    information from the database whenever a template is loaded

    Functions:

    Retrieves and Loads user data for the application Handles POST (Save and
    Submit) Updates the database with new user data through forms Display Error
    Messages when fields are not properly filled

    Check:

    Contains a number of detailed checks which ensure the contents of
    all information being passed from the form, through python and
    eventually into the database

    """

    user_id = session["user_id"]

    # Retrieve the application data for the user from the database and display
    # it by passing it into the template
    if "user_id" in session:

        # Pass in any existing attributes about the user into the template

        priordegreeinfo = get_prior_degree_info(user_id, connect_db())

        # When Submit or Save is pressed
        if request.method == "POST":

            user_id = session["user_id"]

            ## Get Personal Information ##

            firstname = request.form.get("firstname")
            lastname = request.form.get("lastname")
            address = request.form.get("address")
            ssn = request.form.get("ssn")
            phonenumber = request.form.get("phone")

            # Get Academic Information #
            degreessought = request.form.get("SoughtOptions")
            semester = request.form.get("Semester")
            year = request.form.get("Year")

            BS = request.form.getlist("BS")
            MS = request.form.getlist("MS")

            greverbal = request.form.get("greverbal")
            grequantitative = request.form.get("grequantitative")

            greyearofexam = request.form.get("greyearofexam")
            greadvancedscore = request.form.get("greadvancedscore")
            greadvancedsubject = request.form.get("greadvancedsubject")

            areas_interest = request.form.get("areas_interest")

            priorwork = request.form.get("priorwork")

            priorwork_edit = priorwork.replace("'", "\\'\\")

            # Initialize Prior Degrees to avoid errors
            priordegrees = None

            rec_name_one = request.form.get("rec_name_one")
            rec_email_one = request.form.get("rec_email_one")
            rec_name_two = request.form.get("rec_name_two")
            rec_email_two = request.form.get("rec_email_two")
            rec_name_three = request.form.get("rec_name_three")
            rec_email_three = request.form.get("rec_email_three")

            # Transcript
            
            transcript_submission = request.form.get("transcript")

            # Degrees Sought Options Checks
            if degreessought is None:
                degreessought = None

            # Number of Prior Degrees Check

            # If BS is empty, then no prior degrees have been entered
            if len(BS) == 0:
                priordegrees = None

            # If MS contains information, then the user has a MS and a BS
            # (masters requires bachelors)
            if len(MS) > 0:
                priordegrees = degree_info(2, request.form)

            # Else if only the BS contains information, then the user has a
            # BS
            elif len(BS) > 0:
                priordegrees = degree_info(1, request.form)

            # Delete MS from PD if MS is sought

            if degreessought == "MS":
                if priordegrees is None:
                    flash("Please Select A Prior Degree!", "Failed")
                    save_app(
                        user_id,
                        firstname,
                        lastname,
                        address,
                        ssn,
                        phonenumber,
                        priordegrees,
                        degreessought,
                        areas_interest,
                        greverbal,
                        grequantitative,
                        priorwork_edit,
                        greyearofexam,
                        greadvancedscore,
                        greadvancedsubject,
                        semester,
                        year,
                        rec_name_one,
                        rec_email_one,
                        rec_name_two,
                        rec_email_two,
                        rec_name_three,
                        rec_email_three,
                        transcript_submission
                    )
                    if transcript_submission == 'online':
                        static_folder = os.path.join(os.getcwd(), 'static')
                        filepath = os.path.join(static_folder, 'transcript')
                        filename = request.files
                        file = request.files['usertranscript']
                        if file and allowed_file(file.filename):
                            original_filename = secure_filename(file.filename)
                            filename, extension = os.path.splitext(original_filename)
                            filename_with_user_id = filename + str(user_id) + extension
                            file.save(os.path.join(filepath, filename_with_user_id))
                            save_filename(user_id, filename_with_user_id, connect_db())
                            update_transcript_submission_received(user_id, connect_db())
                    elif transcript_submission == 'mail':
                        update_transcript_submission_received(user_id, connect_db())    
                    reset_application(user_id, connect_db())   
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )
                if ("MS" in priordegrees) is True:
                    # for attribute in priordegrees.keys():
                    #     if attribute == "MS":
                    del priordegrees["MS"]
                    pass

            # Check if the user is trying to save the current form information
            if "Save" in request.form:

                try:
                    # Save all current form information
                    save_app(
                        user_id,
                        firstname,
                        lastname,
                        address,
                        ssn,
                        phonenumber,
                        priordegrees,
                        degreessought,
                        areas_interest,
                        greverbal,
                        grequantitative,
                        priorwork_edit,
                        greyearofexam,
                        greadvancedscore,
                        greadvancedsubject,
                        semester,
                        year,
                        rec_name_one,
                        rec_email_one,
                        rec_name_two,
                        rec_email_two,
                        rec_name_three,
                        rec_email_three,
                        transcript_submission
                    )
                    if transcript_submission == 'online':
                        static_folder = os.path.join(os.getcwd(), 'static')
                        filepath = os.path.join(static_folder, 'transcript')
                        filename = request.files
                        file = request.files['usertranscript']
                        if file and allowed_file(file.filename):
                            original_filename = secure_filename(file.filename)
                            filename, extension = os.path.splitext(original_filename)
                            filename_with_user_id = filename + str(user_id) + extension
                            file.save(os.path.join(filepath, filename_with_user_id))
                            save_filename(user_id, filename_with_user_id, connect_db())
                            update_transcript_submission_received(user_id, connect_db())
                    elif transcript_submission == 'mail':
                        update_transcript_submission_received(user_id, connect_db())       
                except Exception as e:
                    print("Something went wrong:", e)
                    flash(e, "Failed")
                    reset_application(user_id, connect_db()) 
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )

                flash("Progress Saved", "Success")

            # Check if the user is trying to submit the current form information
            elif "Submit" in request.form:

                try:
                    save_app(
                        user_id,
                        firstname,
                        lastname,
                        address,
                        ssn,
                        phonenumber,
                        priordegrees,
                        degreessought,
                        areas_interest,
                        greverbal,
                        grequantitative,
                        priorwork_edit,
                        greyearofexam,
                        greadvancedscore,
                        greadvancedsubject,
                        semester,
                        year,
                        rec_name_one,
                        rec_email_one,
                        rec_name_two,
                        rec_email_two,
                        rec_name_three,
                        rec_email_three,
                        transcript_submission
                    )
                    if transcript_submission == 'online':
                        static_folder = os.path.join(os.getcwd(), 'static')
                        filepath = os.path.join(static_folder, 'transcript')
                        filename = request.files
                        file = request.files['usertranscript']
                        if file and allowed_file(file.filename):
                            original_filename = secure_filename(file.filename)
                            filename, extension = os.path.splitext(original_filename)
                            filename_with_user_id = filename + str(user_id) + extension
                            file.save(os.path.join(filepath, filename_with_user_id))
                            save_filename(user_id, filename_with_user_id, connect_db())
                            update_transcript_submission_received(user_id, connect_db())
                    elif transcript_submission == 'mail':
                        update_transcript_submission_received(user_id, connect_db())   
                except Exception as e:
                    print("Something went wrong:", e)
                    flash(e, "Failed")
                    reset_application(user_id, connect_db()) 
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )

                if priordegrees is None:
                    flash(
                        "Prior Degrees is empty!",
                        "Failed",
                    )
                    reset_application(user_id, connect_db()) 
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )

                if len(priordegrees) > 1:
                    if priordegrees["BS"]["year"] >= priordegrees["MS"]["year"]:
                        flash(
                            "A Masters Cannot Be Completed Before a Bachelors!",
                            "Failed",
                        )
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )

                # Null check for all form fields (NOT PHD-REQUIRED FIELDS)
                if not all(
                    [
                        firstname,
                        lastname,
                        address,
                        ssn,
                        phonenumber,
                        priordegrees,
                        degreessought,
                    ]
                ):
                    flash("Please fill in all required fields!", "Failed")
                    reset_application(user_id, connect_db()) 
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )

                if all(x.isalpha() for x in (firstname + lastname)):
                    pass
                else:
                    flash(
                        "Incorrect Name Format, Make sure first name and last name consist of only alphabetical letters.",
                        "Failed",
                    )
                    reset_application(user_id, connect_db()) 
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )

                # Check if the user is seeking a MS, if so delete pd ms they
                # have a prior MS degree
                if degreessought == "MS":
                    if ("MS" in priordegrees) is True:
                        # for attribute in priordegrees.keys():
                        #     if attribute == "MS":
                        del priordegrees["MS"]

                        pass

                # PriorDegrees is a dictionary of dictionaries, we first need to
                # iterate through each dictionary, then we iterate through each
                # attribute and return a tuple of 2 values, from there we check
                # the second value and make sure it is not none or in our case,
                # empty string.
                for degree in priordegrees.keys():
                    for attribute in priordegrees[degree].items():
                        if attribute[1] == "":
                            flash(
                                "Please fill in all required fields under Prior Degrees!",
                                "Failed",
                            )
                            reset_application(user_id, connect_db()) 
                            return render_template(
                                "application.html",
                                user_data=get_app_data(user_id, connect_db()),
                                priordegreeinfoBS=get_degrees(user_id)[0],
                                priordegreeinfoMS=get_degrees(user_id)[1],
                            )

                # Check if the user is seeking a PHD
                if degreessought == "PHD":

                    # Null check for all form fields (INCLUDING PHD-REQUIRED
                    # FIELDS)
                    if not all(
                        [
                            firstname,
                            lastname,
                            address,
                            ssn,
                            phonenumber,
                            priordegrees,
                            degreessought,
                            greverbal,
                            grequantitative,
                        ]
                    ):
                        flash(
                            "Please fill in all required fields! (GRE Scores are required for PHD applicants)",
                            "Failed",
                        )
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )

                    # Check if a PHD applicant has a Masters
                    if ("MS" in priordegrees) == False:
                        flash(
                            "Please fill in all required fields! (Masters and Bachelors degrees are required for PHD applicants)",
                            "Failed",
                        )
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )

                    if (int(greverbal) < 1 or int(greverbal) > 170) or (
                        int(grequantitative) < 1 or int(grequantitative) > 170
                    ):
                        flash("Invalid GRE Score", "Failed")
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )

                # End of PHD Applicant Check

                # Degrees Sought Options Checks
                if degreessought is None:
                    flash("You have to pursue a degree!", "Failed")
                    reset_application(user_id, connect_db()) 
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )

                # Prior Degree Check
                if len(BS) == 0:
                    flash("You must have a Prior Degree!", "Failed")
                    reset_application(user_id, connect_db()) 
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )

                if len(MS) > 0:
                    priordegrees = degree_info(2, request.form)
                elif len(BS) > 0:
                    priordegrees = degree_info(1, request.form)
                else:
                    flash("You must have a prior degree!", "Failed")
                    reset_application(user_id, connect_db()) 
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )

                # Check if inputs are formatted correctly

                # ssn format
                if (
                    len(ssn) == 11
                    and ssn[0:2].isnumeric()
                    and ssn[3] == "-"
                    and ssn[4:5].isnumeric()
                    and ssn[6] == "-"
                    and ssn[7:10].isnumeric()
                ):
                    pass
                else:
                    flash("Invalid SSN", "Failed")
                    reset_application(user_id, connect_db()) 
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )

                # phonenumber format
                if (
                    len(phonenumber) == 12
                    and phonenumber[0:2].isnumeric()
                    and phonenumber[3] == "-"
                    and phonenumber[4:6].isnumeric()
                    and phonenumber[7] == "-"
                    and phonenumber[8:11].isnumeric()
                ):
                    pass
                else:
                    flash("Invalid Phone Number", "Failed")
                    reset_application(user_id, connect_db()) 
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )
                if grequantitative:
                    if greverbal:
                        pass
                    else:
                        flash("Please fill out the other GRE Score!", "Failed")
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )

                if greverbal:
                    if grequantitative:
                        pass
                    else:
                        flash("Please fill out the other GRE Score!", "Failed")
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )

                if grequantitative:
                    if len(grequantitative) > 3 or grequantitative.isalpha():
                        flash("Invalid GRE Score", "Failed")
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )
                    if int(grequantitative) < 1 or int(grequantitative) > 170:
                        flash("Invalid GRE Score", "Failed")
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )
                if greverbal:
                    if len(greverbal) > 3 or greverbal.isalpha():
                        flash("Invalid GRE Score", "Failed")
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )
                    if int(greverbal) < 1 or int(greverbal) > 170:
                        flash("Invalid GRE Score", "Failed")
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )

                if greadvancedscore:
                    if (len(greadvancedscore) < 4) and greadvancedscore[
                        0:2
                    ].isnumeric():
                        pass
                    else:
                        flash("Invalid GRE Advanced Score", "Failed")
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )
                    if int(greadvancedscore) < 1 or int(greadvancedscore) > 120:
                        flash("Invalid GRE Advanced Score", "Failed")
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )

                    if greadvancedsubject == "":
                        flash("GRE Score must have a subject!", "Failed")
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )

                if grequantitative and greverbal:
                    if greyearofexam == "":
                        flash("GRE Score's must have a year!", "Failed")
                        reset_application(user_id, connect_db()) 
                        return render_template(
                            "application.html",
                            user_data=get_app_data(user_id, connect_db()),
                            priordegreeinfoBS=get_degrees(user_id)[0],
                            priordegreeinfoMS=get_degrees(user_id)[1],
                        )
                    else:
                        if (
                            len(greyearofexam) == 4
                            and (greyearofexam)[0:3].isnumeric()
                            and (greyearofexam) < "2025"
                        ):
                            pass
                        else:
                            flash("Invalid GRE Year", "Failed")
                            reset_application(user_id, connect_db()) 
                            return render_template(
                                "application.html",
                                user_data=get_app_data(user_id, connect_db()),
                                priordegreeinfoBS=get_degrees(user_id)[0],
                                priordegreeinfoMS=get_degrees(user_id)[1],
                            )

                for degree in priordegrees.keys():
                    for attribute in priordegrees[degree].items():
                        if attribute[0] == "year":
                            if (
                                len(attribute[1]) == 4
                                and (attribute[1])[0:3].isnumeric()
                                and (attribute[1]) < "2025"
                            ):
                                pass
                            else:
                                flash("Invalid Prior Degree Year", "Failed")
                                reset_application(user_id, connect_db()) 
                                return render_template(
                                    "application.html",
                                    user_data=get_app_data(user_id, connect_db()),
                                    priordegreeinfoBS=get_degrees(user_id)[0],
                                    priordegreeinfoMS=get_degrees(user_id)[1],
                                )

                for degree in priordegrees.keys():
                    for attribute in priordegrees[degree].items():
                        if attribute[0] == "gpa":
                            if (
                                len(attribute[1]) == 4
                                and (attribute[1])[0].isnumeric()
                                and (attribute[1])[1] == "."
                                and (attribute[1])[2:3].isnumeric()
                                and (attribute[1]) <= "4.00"
                            ):
                                pass
                            else:
                                flash("Invalid Prior Degree GPA", "Failed")
                                reset_application(user_id, connect_db()) 
                                return render_template(
                                    "application.html",
                                    user_data=get_app_data(user_id, connect_db()),
                                    priordegreeinfoBS=get_degrees(user_id)[0],
                                    priordegreeinfoMS=get_degrees(user_id)[1],
                                )
                if not all([rec_name_one, rec_email_one]):
                    flash("You must have a recommender", "Failed")
                    reset_application(user_id, connect_db()) 
                    return render_template(
                        "application.html",
                        user_data=get_app_data(user_id, connect_db()),
                        priordegreeinfoBS=get_degrees(user_id)[0],
                        priordegreeinfoMS=get_degrees(user_id)[1],
                    )
                # end of checkformat

                submit_app(
                    user_id,
                    connect_db(),
                )

                flash("Succesfully Submitted!", "Success")

                email_recommenders(user_id, session['first_name'], session['last_name'],
                                rec_name_one,
                                rec_email_one,
                                rec_name_two,
                                rec_email_two,
                                rec_name_three,
                                rec_email_three, connect_db())

                return redirect(url_for("applicanthome"))

            else:
                return

        return render_template(
            "application.html",
            user_data=get_app_data(user_id, connect_db()),
            priordegreeinfoBS=get_degrees(user_id)[0],
            priordegreeinfoMS=get_degrees(user_id)[1],
        )

    return render_template(
        "application.html",
        user_data=get_app_data(user_id, connect_db()),
        priordegreeinfoBS=get_degrees(user_id)[0],
        priordegreeinfoMS=get_degrees(user_id)[1],
    )


# Where faculty reviewers are able to view the completed
# applications submitted by applicants
@app.route("/viewapplication/<applicationid>", methods=["GET", "POST"])
def viewapplication(applicationid):
    """Displays an application along with the contents entered by the applicant"""

    user_id = session["user_id"]

    return render_template(
        "viewapplication.html",
        user_data=get_app_data_appid(applicationid, connect_db()),
        priordegreeinfoBS=get_degrees_appid(applicationid)[0],
        priordegreeinfoMS=get_degrees_appid(applicationid)[1],
    )


# Where a user is able to view their usernname, and email,
# and begin an application or logout
@app.route("/userhome", methods=["GET", "POST"])
def userhome():
    """Contains the options that users will have : Only have the option of
    applying"""

    if request.method == "POST":

        if "Apply" in request.form:

            return redirect(url_for("application"))
        if "Logout" in request.form:

            return redirect(url_for("logout"))

    return render_template("userhome.html")


# Where an applicant is able to review the status and recommendation letter
# associated with their application
@app.route("/applicanthome", methods=["GET", "POST"])
def applicanthome():
    """Contains the options that applicants will have : Can check the status of
    their application"""

    # Grab the appid
    user_id = session["user_id"]
    app_data = get_app_data(user_id, connect_db())
    app_status = get_app_status(connect_db(), user_id)

    # Set the applicationid
    session["applicationid"] = app_data["applicationid"]

    # Grab the role
    userrolerow = grab_role(user_id, connect_db())
    session["role"] = userrolerow["role"]

    uid = get_uid(user_id, connect_db())

    session["studentid"] = uid["uid"]

    # Grab the application status
    session["status"] = str(app_status)

    if request.method == "POST":

        if "Status" in request.form:

            return redirect(url_for("status"))

        if "Submit" in request.form:

            return redirect(url_for("application"))

        if "Recommendation" in request.form:

            return redirect(url_for("recommendation"))

    return render_template(
        "applicanthome.html",
        status=get_app_status(connect_db(), user_id),
        decision=get_decision(user_id, connect_db()),
    )


# Where an applicant is able to fill out a recommendation letter
# simulating the existence of an external recommender
@app.route("/recommendation", methods=["GET", "POST"])
def recommendation():

    if request.method == "POST":

        rec_name_one = request.form.get("rec_name_one")
        rec_email_one = request.form.get("rec_email_one")
        rec_letter_one = request.form.get("rec_letter_one")
        rec_name_two = request.form.get("rec_name_two")
        rec_email_two = request.form.get("rec_email_two")
        rec_letter_two = request.form.get("rec_letter_two")
        rec_name_three = request.form.get("rec_name_three")
        rec_email_three = request.form.get("rec_email_three")
        rec_letter_three = request.form.get("rec_letter_three")
        user_id = session["user_id"]

        if "Submit" in request.form:

            # Checks for form
            if not all([rec_name_one, rec_name_one, rec_name_one]):
                flash("Please fill in all required fields!", "Failed")
                return redirect(url_for("recommendation"))
            else:
                db = connect_db()
                cursor = db.cursor()

                updaterec = "UPDATE recommendationletter SET rec_letter = %s, status = 'received' WHERE user_id = %s"

                updaterecvalues = (rec_name_one, user_id)

                cursor.execute(updaterec, updaterecvalues)

                flash("Recommendation Letter Submitted!", "Success")

            # If there are no form errors
            return render_template(
                "applicanthome.html",
                rec_info=get_rec_info(session["user_id"], connect_db()),
            )

        if "Return" in request.form:

            return redirect(url_for("applicanthome"))

    return render_template(
        "recommendation.html", rec_info=get_rec_info(session["user_id"], connect_db())
    )


# Where faculty reviewers are able to review recommendation letters submitted by
# applicant-selected recommenders
@app.route("/recommendationletter/<user_id>", methods=["GET", "POST"])
def recommendationletter(user_id):
    """Displays the recommendation letter associated with the given user_id"""

    return render_template(
        "recommendationletter.html", rec_info=get_rec_info(user_id, connect_db())
    )


# Chair, Reviewers : List of applications that are ready to review, this means
# that the recommendation letter, transcript are all received for it to appear
# in this table.
@app.route("/reviewhome", methods=["GET", "POST"])
def reviewhome():
    """List of Applications that are ready to review"""

    user_id = session["user_id"]

    applications = get_pending_review_apps(user_id, connect_db())
    reviewed = has_reviewed(user_id, connect_db())
        

    return render_template("reviewhome.html", applications = applications, reviewed = reviewed)
@app.route("/view_reviews", methods=["GET", "POST"])
def view_reviews():
    all_reviews = get_all_reviews(connect_db())

    search_query = request.args.get('search')
    if search_query:
        all_reviews = get_all_reviews_by_user_id(search_query, connect_db())
        query = True


        

    return render_template("view_reviews.html", all_reviews = all_reviews, query = True)
@app.route("/cachome", methods=["GET", "POST"])
def cachome():
    """List of Applications that are ready to review"""

    user_id = session["user_id"]

    applications = get_pending_review_apps(user_id, connect_db())
    
        

    return render_template("cachome.html", applications = applications)
# Where an admin is able to view, select for edit, or delete any user within the system
@app.route("/adminhome", methods=["GET", "POST"])
def adminhome():
    """Displays all current users in the database, along with the options
    to edit, or delete any user except for the admin account currently viewing the page
    """
    message = None
    user_data=get_users(connect_db())

    if request.method == "POST":

        if request.form.get('Delete'):
            user_id = request.form.get("Delete")
            role = get_user_role(user_id, connect_db())

            if int(user_id) != session["user_id"]:

                delete_user(user_id, role, connect_db())
                message = "User Successfully Removed!"
            else:
                message= "You cannot remove your own account!"

            return render_template(
                "adminhome.html", user_data=user_data, message = message
            )

    return render_template("adminhome.html", user_data=user_data, message = message)


@app.route("/admin_assign_advisor", methods=["GET", "POST"])
def admin_assign_advisor():
    message = None
    students = get_all_students(connect_db())
    advisors = get_all_advisors(connect_db())


    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_advisor_id = request.form.get("new_advisor")
        if new_advisor_id:
            set_advisor(new_advisor_id, user_id, connect_db())

    search_query = request.args.get('search')
    if search_query:
        digit_pattern = r'^\d{8}$'
        name_pattern = r'^[A-Za-z]+$'
        if re.match(digit_pattern, search_query):
            students = get_student_information_by_uid(search_query, connect_db())
        elif re.match(name_pattern, search_query):
            students = get_student_information_by_lname(search_query, connect_db())
        else:
            message = "Invalid search input. Please enter an 8-digit UID or a last name."


    return render_template(
        "admin_assign_advisor.html", students = students, advisors = advisors, message =message
    )



# allows for a new user to be add to the database given the necessary info
@app.route("/adduser", methods=["GET", "POST"])
def adduser():
    """Add a new user to the database (from sysadmin)"""

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        address = request.form.get('address')
        dob = request.form.get('dob')
        role = request.form.get('roles')
        admin_adduser(email, username, password, fname, lname, address, dob, role, connect_db())


    return render_template("adduser.html")



# Where an Admin is able to edit the roles of specific users
@app.route("/edituser/<user_id>", methods=["GET", "POST"])
def edit(user_id):
    """Page which displays a selected user, their role, and a drop down
    of roles for reassignment"""

    user_data = get_user_info(user_id, connect_db())

    if request.method == "POST":

        requestedrole = request.form.get("roles")

        # Update the user's role
        change_user_role(user_id, requestedrole, connect_db())

        # Update session variables
        # update_session_variables(user_id, session)

        return render_template(
            "edituser.html", user=get_user_info(user_id, connect_db())
        )

    return render_template("edituser.html", user=user_data)


# Faculty is able to view information pertaining to a specific student
# Transcript, Recommendation Letter,  and Application. While also gaining access
# to the review form
@app.route("/studentinfo/<user_id>", methods=["GET", "POST"])
def studentinfo(user_id):
    """Where a reviewer can view all elements of an application"""

    app_info = get_app_data(user_id, connect_db())

    if request.method == "POST":
        action = request.form.get("Submit")

        if action == "transcript":
            if app_info['transcript_submission'] == 'mail':
                return redirect("/static/transcript/transcript2.pdf")
            elif app_info['transcript_submission'] == 'email':
                static_folder = os.path.join(os.getcwd(), 'static')
                filepath = os.path.join(static_folder, 'transcript')

                filename = get_filename(user_id, connect_db())

                files_in_folder = os.listdir(filepath)

                for file_in_folder in files_in_folder:
                    if file_in_folder == filename:
                        return redirect("/static/transcript/" + filename)
            elif app_info['transcript_submission'] == 'online':
                static_folder = os.path.join(os.getcwd(), 'static')
                filepath = os.path.join(static_folder, 'transcript')

                filename = get_filename(user_id, connect_db())

                files_in_folder = os.listdir(filepath)
                for file_in_folder in files_in_folder:
                    if file_in_folder == filename:
                        return redirect("/static/transcript/" + filename)
        elif action == "rec":
            return redirect(url_for("recommendationletter", user_id=user_id))
        elif action == "view":
            return redirect(
                url_for(
                    "viewapplication", applicationid=get_app_id(connect_db(), user_id)
                )
            )
        elif action == "form":
            return redirect(url_for("reviewform", user_id=user_id))
        elif action == "return":
            return redirect(url_for("reviewhome"))

    return render_template(
        "studentinfo.html",
        app_info=app_info,
        transcript_status=get_transcript_status(user_id, connect_db()),
        rec_status=get_rec_status(user_id, connect_db()),
    )


# Graduate Secretary, Views the Transcript, Recommendation Letter, Uneditable Application and
# Uneditable Review Form (Besides the final decision) of a student.
@app.route("/gsc_studentinfo", methods=["GET", "POST"])
def gsc_studentinfo():
    """Returns a template with Transcript, Rec Letter, Application and Review Form"""

    user_id = request.args.get("user_id")
    reviewerid = request.args.get("reviewerid")
    app_info = get_app_data(user_id, connect_db())
    app_id = app_info["applicationid"]

    if request.method == "POST":

        action = request.form.get("Submit")

        if action == "transcript":
            if app_info['transcript_submission'] == 'mail':
                return redirect("/static/transcript/transcript2.pdf")
            elif app_info['transcript_submission'] == 'email':
                static_folder = os.path.join(os.getcwd(), 'static')
                filepath = os.path.join(static_folder, 'transcript')

                filename = get_filename(user_id, connect_db())

                files_in_folder = os.listdir(filepath)

                for file_in_folder in files_in_folder:
                    if file_in_folder == filename:
                        return redirect("/static/transcript/" + filename)
            elif app_info['transcript_submission'] == 'online':
                static_folder = os.path.join(os.getcwd(), 'static')
                filepath = os.path.join(static_folder, 'transcript')

                filename = get_filename(user_id, connect_db())

                files_in_folder = os.listdir(filepath)
                for file_in_folder in files_in_folder:
                    if file_in_folder == filename:
                        return redirect("/static/transcript/" + filename)
        elif action == "rec":
            return redirect(url_for("recommendationletter", user_id=user_id))
        elif action == "view":
            return redirect(url_for("viewapplication", applicationid=app_id))
        elif action == "form":
            return redirect(
                url_for("viewreviewform", applicationid=app_id, reviewerid=reviewerid)
            )
        elif action == "refresh":

            refresh_email(user_id, connect_db())

            return render_template(
            "gsc_studentinfo.html",
            app_info=app_info,
            rev_status=get_review_status(app_id, connect_db()),
            transcript_status=get_transcript_status(user_id, connect_db()),
            rec_status=get_rec_status(user_id, connect_db()),
            reviewerid=reviewerid,
            )
        elif action == "return":
            return redirect(url_for("gschome"))

    return render_template(
        "gsc_studentinfo.html",
        app_info=app_info,
        rev_status=get_review_status(app_id, connect_db()),
        transcript_status=get_transcript_status(user_id, connect_db()),
        rec_status=get_rec_status(user_id, connect_db()),
        reviewerid=reviewerid,
    )
@app.route("/adv_studentinfo", methods=["GET", "POST"])
def adv_studentinfo():
    """Returns a template with Transcript, Rec Letter, Application and Review Form"""

    user_id = request.args.get("user_id")
    reviewerid = request.args.get("reviewerid")
    app_info = get_app_data(user_id, connect_db())
    app_id = app_info["applicationid"]

    if request.method == "POST":

        action = request.form.get("Submit")

        if action == "transcript":
            if app_info['transcript_submission'] == 'mail':
                return redirect("/static/transcript/transcript2.pdf")
            elif app_info['transcript_submission'] == 'email':
                static_folder = os.path.join(os.getcwd(), 'static')
                filepath = os.path.join(static_folder, 'transcript')

                filename = get_filename(user_id, connect_db())

                files_in_folder = os.listdir(filepath)

                for file_in_folder in files_in_folder:
                    if file_in_folder == filename:
                        return redirect("/static/transcript/" + filename)
            elif app_info['transcript_submission'] == 'online':
                static_folder = os.path.join(os.getcwd(), 'static')
                filepath = os.path.join(static_folder, 'transcript')

                filename = get_filename(user_id, connect_db())

                files_in_folder = os.listdir(filepath)
                for file_in_folder in files_in_folder:
                    if file_in_folder == filename:
                        return redirect("/static/transcript/" + filename)
        elif action == "rec":
            return redirect(url_for("recommendationletter", user_id=user_id))
        elif action == "view":
            return redirect(url_for("viewapplication", applicationid=app_id))
        elif action == "form":
            return redirect(
                url_for("viewreviewform", applicationid=app_id, reviewerid=reviewerid)
            )
        elif action == "refresh":

            refresh_email(user_id, connect_db())

            return render_template(
            "adv_studentinfo.html",
            app_info=app_info,
            rev_status=get_review_status(app_id, connect_db()),
            transcript_status=get_transcript_status(user_id, connect_db()),
            rec_status=get_rec_status(user_id, connect_db()),
            reviewerid=reviewerid,
            )
        elif action == "return":
            return redirect(url_for("advisor_dashboard"))

    return render_template(
        "adv_studentinfo.html",
        app_info=app_info,
        rev_status=get_review_status(app_id, connect_db()),
        transcript_status=get_transcript_status(user_id, connect_db()),
        rec_status=get_rec_status(user_id, connect_db()),
        reviewerid=reviewerid,
    )


# Chair and Graduate Secretary, A reviewform that is ready for final decisions to be made, cannot edit the previously reviewed entries
@app.route("/viewreviewform/<applicationid>", methods=["GET", "POST"])
def viewreviewform(applicationid):
    """Returns a reviewform based on the application id, this reviewform can not be edited and only the final decision can be changed"""

    user_id = session["user_id"]
    reviewerid = request.args.get("reviewerid")

    final_decision = request.form.get("final_decision")

    if request.method == "POST":

        if "Submit" in request.form:

            set_final_decision(final_decision, applicationid, connect_db())

            flash("Final Decision has been made!", "Success")

            return redirect(url_for("gschome"))

    if reviewerid:

        return render_template(
            "viewreviewform.html",
            appinfo=get_app_data_appid(applicationid, connect_db()),
            degree_info=get_prior_degree_info_appid(applicationid, connect_db()),
            review_info=get_review_for_reviewer(
                applicationid, reviewerid, connect_db()
            ),
        )

    else:

        return render_template(
            "viewreviewform.html",
            appinfo=get_app_data_appid(applicationid, connect_db()),
            degree_info=get_prior_degree_info_appid(applicationid, connect_db()),
            review_info=get_review_info(applicationid, connect_db()),
        )


# Chairs and Reviewers, View the review form based on the application, Based on the user_id of an applicant
@app.route("/reviewform/<user_id>", methods=["GET", "POST"])
def reviewform(user_id):
    """Return a reviewform based on the user_id of an applicant"""

    applicationinfo = get_app_data(user_id, connect_db())

    reviewerid = session["user_id"]

    rating = request.form.get("rating")
    generic = request.form.get("generic")
    credible = request.form.get("Credible")

    gas_decision = request.form.get("gas_decision")
    missing_course = request.form.get("missing_course")
    reasons_reject = request.form.get("reasons_reject")
    reviewer_comment = request.form.get("reviewer_comment")
    recommended_advisor = request.form.get("recommended_advisor")

    final_decision = request.form.get("final_decision")

    if request.method == "POST":

        if "Submit" in request.form:

            if session["role"] == "cac":
                if gas_decision is None:
                    flash("Please make a final decision!", "Failed")
                    return render_template(
                        "reviewform.html",
                        appinfo=applicationinfo,
                        degree_info=get_prior_degree_info(user_id, connect_db()),
                    )
                else:
                    submit_review(
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
                        connect_db(),
                    )
                    if gas_decision:
                        flash("Reivew Form Submitted!", "Success")
                    if final_decision:
                        flash("Final decision has been made!", "Success")
                        set_final_decision(final_decision, user_id, connect_db())

                    return redirect(url_for("reviewhome"))

            if gas_decision == None:

                flash("Please make a decision!", "Failed")

                return render_template(
                    "reviewform.html",
                    appinfo=applicationinfo,
                    degree_info=get_prior_degree_info(user_id, connect_db()),
                )
            else:

                submit_review(
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
                    connect_db(),
                )

                flash("Review Form Submitted!", "Success")

                return redirect(url_for("reviewhome"))

        elif "ReturnToRevHome" in request.form:

            return render_template(
                "studentinfo.html",
                app_info=get_app_data(user_id, connect_db()),
                appinfo=get_app_data(user_id, connect_db()),
                degree_info=get_prior_degree_info(user_id, connect_db()),
            )

    return render_template(
        "reviewform.html",
        appinfo=applicationinfo,
        degree_info=get_prior_degree_info(user_id, connect_db()),
    )

@app.route("/reghome", methods=["GET", "POST"])
def reghome():

    courses = get_all_courses(connect_db())
    instructors = get_instructors(connect_db())
    if request.method == 'POST':
        if request.form.get('remove_course'):
            print("REMOVE")
            crn = request.form.get('remove_course')
            remove_course_crn(crn, connect_db())
        if request.form.get('add_course'):
            course = request.form.get('course')
            num = course.split("_")[1]
            dept = course.split("_")[0]

            day = request.form.get('day')

            time = request.form.get('time')
            start = time.split("_")[0]
            end = time.split("_")[1]

            instructor = request.form.get('instructor')
            semester = request.form.get('semester')
            year = request.form.get('year')
            add_course(dept, num, day, start, end, instructor, semester, year, connect_db())

    return render_template(
        "reghome.html", courses = courses, instructors=instructors
    )
# Graduate Secreatary and Chair, This is the default page for Graduate Seecretaries which allows for the final decisions to be amde
@app.route("/gschome", methods=["GET", "POST"])
def gschome():
    """Sets the final decisions for review forms"""
    

    return render_template(
        "gschome.html", review_info=get_pending_review_form(connect_db())
    )
@app.route("/assign_advisor", methods=["GET", "POST"])
def assign_advisor():
    message = None
    students = get_all_students(connect_db())
    advisors = get_all_advisors(connect_db())


    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_advisor_id = request.form.get("new_advisor")
        if new_advisor_id:
            set_advisor(new_advisor_id, user_id, connect_db())

    search_query = request.args.get('search')
    if search_query:
        digit_pattern = r'^\d{8}$'
        name_pattern = r'^[A-Za-z]+$'
        if re.match(digit_pattern, search_query):
            students = get_student_information_by_uid(search_query, connect_db())
        elif re.match(name_pattern, search_query):
            students = get_student_information_by_lname(search_query, connect_db())
        else:
            message = "Invalid search input. Please enter an 8-digit UID or a last name."


    return render_template(
        "assign_advisor.html", students = students, advisors = advisors, message =message
    )
@app.route("/students", methods=["GET", "POST"])
def students():
    message = None
    students = get_all_students(connect_db())

    search_query = request.args.get('search')
    if search_query:
        digit_pattern = r'^\d{8}$'
        name_pattern = r'^[A-Za-z]+$'
        if re.match(digit_pattern, search_query):
            students = get_student_information_by_uid(search_query, connect_db())
        elif re.match(name_pattern, search_query):
            students = get_student_information_by_lname(search_query, connect_db())
        else:
            message = "Invalid search input. Please enter an 8-digit UID or a last name."

    if request.form.get('filter_input'):
            filter = request.form.get('filter')
            if filter == 'semester':
                semester = request.form.get('semester')
                students = filter_students_semester(semester, connect_db())
            if filter == 'year':
                year = request.form.get('year')
                students = filter_students_year(year, connect_db())
            if filter == 'program':
                program = request.form.get('program')
                students = filter_students_program(program, connect_db())
            if filter == 'cleared_to_graduate':
                students = filter_students_cleared_graduate(connect_db())
    return render_template(
        "students.html", students = students
    )
@app.route("/student/<user_id>", methods=["GET", "POST"])
def student(user_id):
    message = None
    uid = get_university_id(user_id, connect_db())['uid']
    student = get_student_information_by_uid(uid, connect_db())
    courses_taken = get_courses_taken(uid, connect_db())
    form_one = get_form_one(uid, connect_db())
    forms_classes = get_form_classes(uid, connect_db())
    thesis = get_thesis(uid, connect_db())
    graduation_application = get_graduation_application(uid, connect_db())

    if request.method == 'POST':
        if request.form.get('student_uid'):
            student_uid = request.form.get('student_uid')
            new_grade = request.form.get('new_grade')
            crn = request.form.get('course_crn')
            update_grade(student_uid, new_grade, crn, connect_db())
            return render_template("student.html", message=message,student=student,courses_taken=courses_taken,form_one=form_one,forms_classes=forms_classes,thesis=thesis,graduation_application=graduation_application)
        if request.form.get('approve'):
            uid = request.form.get('approve_uid')
            approve_form_one(uid, connect_db())
        if request.form.get('clear_graduation'):
            uid = request.form.get('graduation_uid')
            if not graduation_application:
                message = "Student has not submitted a graduation application!"
                return render_template("student.html", message=message,student=student,courses_taken=courses_taken,form_one=form_one,forms_classes=forms_classes,thesis=thesis,graduation_application=graduation_application)
            approve_graduation(uid, connect_db())
        

    return render_template(
        "student.html", message=message,student=student,courses_taken=courses_taken,form_one=form_one,forms_classes=forms_classes,thesis=thesis,graduation_application=graduation_application
    )
# For Chair and Graduate Secretaries, they are able to update the system on the status of an applications transcript
@app.route("/applications", methods=["GET", "POST"])
def applications():

    message = None
    all_application=get_all_full_applications(connect_db())
    if request.method == "POST":

        if request.form.get('filter_input'):
            filter = request.form.get('filter')
            if filter == 'semester':
                semester = request.form.get('semester')
                all_application = filter_application_semester(semester, connect_db())
            if filter == 'year':
                year = request.form.get('year')
                all_application = filter_application_year(year, connect_db())
            if filter == 'program':
                program = request.form.get('program')
                all_application = filter_application_program(program, connect_db())
        if request.form.get('confirm'):
            user_id = request.form.get("user_id")
            new_transcript = request.form.get("new_transcript_status_" + user_id)
            if new_transcript:
                status = new_transcript.split("Update to ")[1].lower()
                set_transcript_status(status, user_id, connect_db())
    
    search_query = request.args.get('search')
    if search_query:
        digit_pattern = r'^\d{8}$'
        name_pattern = r'^[A-Za-z]+$'
        if re.match(digit_pattern, search_query):
            all_application = get_full_application_by_uid(search_query, connect_db())
        elif re.match(name_pattern, search_query):
            all_application = get_full_application_by_lname(search_query, connect_db())
        else:
            message = "Invalid search input. Please enter an 8-digit UID or a last name."
    


    stats = application_stats(all_application)
    return render_template(
        "applications.html", all_application = all_application, message = message, stats = stats
    )


# For Applicants, check the current status of the application
@app.route("/status", methods=["GET", "POST"])
def status():
    """Gets the status based on the user_id"""

    # application incomplete -- application complete -- under review decision
    # DEFAULT 'application incomplete'

    user_id = session["user_id"]

    if request.method == "POST":

        if "Home" in request.form:

            return redirect(url_for("applicanthome"))

    return render_template(
        "applicantstatus.html",
        status=get_app_status(connect_db(), user_id),
        decision=get_decision(user_id, connect_db()),
    )


# All Users, Handles a user's logout process by clearing all session variables and redirecting to the login page
@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Cleans up session variables : username , email, role, question_history, and response_history when logout is pressed"""

    admitted = request.args.get('admitted')

    if admitted:
        admit(session['user_id'], connect_db())

    clear_session(session)

    if request.method == "POST":
        if "Logout" in request.form:
            redirect("/")

    return redirect("/")


# Helper Function, Deletes all information in the database and replaces it with "Start Data"
@app.route("/reset", methods=["GET", "POST"])
def reset():
    """Reset the database completely"""

    reset_database()

    return redirect("/")


# Applicant and Users, Handles questions and responses by using gemini, keeps track of history and provides context to questions
@app.route("/voiceassistant", methods=["GET", "POST"])
def voiceassistant():
    """Returns a response based on a PDF file that gives the ai some context, not perfect"""

    genai.configure(api_key="AIzaSyAaKikwWsS_r67Qzya8D_muscRa5jXJE3g")
    model = genai.GenerativeModel("gemini-pro")

    userrolerow = grab_role(session["user_id"], connect_db())
    userrole = userrolerow["role"]

    with open("static/context/context.pdf", "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        context = ""
        for page in pdf_reader.pages:
            context += page.extract_text()

    question = request.form.get("question")

    config = {"max_output_tokens": 300, "temperature": 0.9, "top_p": 1, "top_k": 32}

    response = model.generate_content([context, question], generation_config=config)

    try:
        response = response.text
    except Exception as e:
        response = "Unfortunately, I cannot answer that question at the moment"

    if ("user_id" or "user id") in question:
        response = "\n I noticed you're asking about a user_id! \nYours is: " + str(
            get_uid(session["user_id"], connect_db())["uid"]
        )

    question_history = session.get("question_history", [])
    response_history = session.get("response_history", [])

    question_history.append(question)
    response_history.append(response)

    session["question_history"] = question_history
    session["response_history"] = response_history

    session["question"] = question
    session["response"] = response

    if userrole == "applicant":

        return render_template(
            "applicanthome.html",
            history=zip(session["question_history"], session["response_history"]),
        )

    elif userrole == "user":
        return render_template(
            "userhome.html",
            history=zip(session["question_history"], session["response_history"]),
        )
    else:
        return redirect(request.referrer)




# allows an admin to view completed review forms in the case a reviewer wants to redo a review form
@app.route("/adminreview", methods=["GET", "POST"])
def adminreview():
    """Allows an admin to view completed review forms in the case a reviewer wants to redo a review form"""

    if request.method == "POST":
        app_id = request.form.get("select")
        review_status = request.form.get("review_status")
        reviewer_id = request.form.get("reviewer_id")
        reviewid = request.form.get("delete")

        # pull current data
        review_data = get_all_reviewed_info(connect_db())
        if len(review_data) == 0:
            review_data = None

        if reviewid and (review_status == "reviewed"):

            # get rid of specified review form
            delete_reviewform(reviewer_id, reviewid, connect_db())

            # pull current data reflecting recent review form removal
            review_data = get_all_reviewed_info(connect_db())
            if len(review_data) == 0:
                review_data = None

            # return
            return render_template(
                "adminreview.html",
                review_data=review_data,
                review=None,
            )

        return render_template(
            "adminreview.html",
            review_data=review_data,
            review=get_review_info(app_id, connect_db()),
        )

    review_data = get_all_reviewed_info(connect_db())
    if len(review_data) == 0:
        review_data = None

    return render_template("adminreview.html", review_data=review_data, review=None)
@app.route("/search_applicant", methods=["GET", "POST"])
def search_applicant(db, search_term):
    cursor = db.cursor()

    # Search for an applicant using their last name or student number
    query = """
    SELECT u.email, a.applicationid
    FROM application a
    INNER JOIN user u ON a.user_id = u.user_id
    WHERE u.last_name = %s OR a.uid = %s;
    """
    cursor.execute(query, (search_term, search_term))
    result = cursor.fetchall()
    return result

@app.route("/update_applicant_info", methods=["GET", "POST"])
def update_applicant_info(db, user_id, new_info):
    cursor = db.cursor()

    # Update applicant's academic and personal information
    # Assuming new_info is a dictionary containing the updated information
    update_query = """
    UPDATE application
    SET first_name = %s, last_name = %s, address = %s
    WHERE user_id = %s;
    """
    cursor.execute(update_query, (new_info['first_name'], new_info['last_name'], new_info['address'], user_id))
    db.commit()

@app.route("/update_user_info", methods=["GET", "POST"])
def update_user_info(db, user_id, new_info):
    cursor = db.cursor()

    # Update user's personal information
    # Assuming new_info is a dictionary containing the updated information
    update_query = """
    UPDATE user
    SET first_name = %s, last_name = %s, address = %s
    WHERE user_id = %s;
    """
    cursor.execute(update_query, (new_info['first_name'], new_info['last_name'], new_info['address'], user_id))
    db.commit()

@app.route("/generate_graduate_applicants_list", methods=["GET", "POST"])
def generate_graduate_applicants_list(db, semester=None, year=None, degree_program=None):
    cursor = db.cursor()

    # Generate the list of graduate applicants based on semester, year, or degree program
    if semester and year:
        query = """
        SELECT u.email
        FROM application a
        INNER JOIN user u ON a.user_id = u.user_id
        WHERE a.semester = %s AND a.year = %s AND a.degreessought = 'MS' OR a.degreessought = 'PhD';
        """
        cursor.execute(query, (semester, year))
    elif degree_program:
        query = """
        SELECT u.email
        FROM application a
        INNER JOIN user u ON a.user_id = u.user_id
        WHERE a.degreessought = %s;
        """
        cursor.execute(query, (degree_program,))
    else:
        return None

    result = cursor.fetchall()
    return result

@app.route("/generate_admitted_students_list", methods=["GET", "POST"])
def generate_admitted_students_list(db, semester=None, year=None, degree_program=None):
    cursor = db.cursor()

    # Generate the list of admitted students based on semester, year, or degree program
    if semester and year:
        query = """
        SELECT u.email
        FROM application a
        INNER JOIN user u ON a.user_id = u.user_id
        WHERE a.semester = %s AND a.year = %s AND a.decision = 'admit';
        """
        cursor.execute(query, (semester, year))
    elif degree_program:
        query = """
        SELECT u.email
        FROM application a
        INNER JOIN user u ON a.user_id = u.user_id
        WHERE a.degreessought = %s AND a.decision = 'admit';
        """
        cursor.execute(query, (degree_program,))
    else:
        return None

    result = cursor.fetchall()
    return result

@app.route("/generate_statistics", methods=["GET", "POST"])
def generate_statistics(db, semester=None, year=None, degree_program=None):
    cursor = db.cursor()

    # Generate statistics such as total number of applicants, admitted, rejected, and average GRE score for admitted
    if semester and year:
        query = """
        SELECT COUNT(*) AS total_applicants,
               SUM(CASE WHEN decision = 'admit' THEN 1 ELSE 0 END) AS admitted,
               SUM(CASE WHEN decision = 'reject' THEN 1 ELSE 0 END) AS rejected,
               AVG(CASE WHEN decision = 'admit' THEN greverbal + grequantitative ELSE NULL END) AS avg_gre_score
        FROM application
        WHERE semester = %s AND year = %s;
        """
        cursor.execute(query, (semester, year))
    elif degree_program:
        query = """
        SELECT COUNT(*) AS total_applicants,
               SUM(CASE WHEN decision = 'admit' THEN 1 ELSE 0 END) AS admitted,
               SUM(CASE WHEN decision = 'reject' THEN 1 ELSE 0 END) AS rejected,
               AVG(CASE WHEN decision = 'admit' THEN greverbal + grequantitative ELSE NULL END) AS avg_gre_score
        FROM application
        WHERE degreessought = %s;
        """
        cursor.execute(query, (degree_program,))
    else:
        return None

    result = cursor.fetchone()
    return result

@app.route("/generate_graduating_students_list", methods=["GET", "POST"])
def generate_graduating_students_list(db, semester=None, year=None):
    cursor = db.cursor()

    # Generate the list of graduating students based on semester or year
    if semester and year:
        query = """
        SELECT u.email
        FROM student s
        INNER JOIN user u ON s.user_id = u.user_id
        WHERE s.graduation_semester = %s AND s.graduation_year = %s;
        """
        cursor.execute(query, (semester, year))
    else:
        return None

    result = cursor.fetchall()
    return result

@app.route("/generate_alumni_list", methods=["GET", "POST"])
def generate_alumni_list(db):
    cursor = db.cursor()

    # Generate the list of alumni and their email addresses
    query = """
    SELECT u.email
    FROM alumni a
    INNER JOIN user u ON a.user_id = u.user_id;
    """
    cursor.execute(query)
    result = cursor.fetchall()
    return result

@app.route("/generate_current_students_list", methods=["GET", "POST"])
def generate_current_students_list(db, degree=None, admit_year=None):
    cursor = db.cursor()

    # Generate the total list of current students by degree or admit year
    if degree:
        query = """
        SELECT u.email
        FROM student s
        INNER JOIN user u ON s.user_id = u.user_id
        WHERE s.program = %s;
        """
        cursor.execute(query, (degree,))
    elif admit_year:
        query = """
        SELECT u.email
        FROM application a
        INNER JOIN user u ON a.user_id = u.user_id
        WHERE a.year = %s;
        """
        cursor.execute(query, (admit_year,))
    else:
        return None

    result = cursor.fetchall()
    return result

@app.route("/change_advisor", methods=["GET", "POST"])
def change_advisor(db, student_uid, new_advisor_id):
    cursor = db.cursor()

    # Change the advisor for a student given the student's student number
    update_query = """
    UPDATE student
    SET advisor_id = %s
    WHERE uid = %s;
    """
    cursor.execute(update_query, (new_advisor_id, student_uid))
    db.commit()

@app.route("/generate_transcript", methods=["GET", "POST"])
def generate_transcript(db, student_uid):
    cursor = db.cursor()

    # Generate the transcript for a student given their student number
    query = """
    SELECT ct.course_title, ct.credits, ct.grade
    FROM course_taken ct
    INNER JOIN student s ON ct.university_id = s.uid
    WHERE s.uid = %s;
    """
    cursor.execute(query, (student_uid,))
    result = cursor.fetchall()
    return result

@app.route("/generate_advisees_list", methods=["GET", "POST"])
def generate_advisees_list(db, advisor_id):
    cursor = db.cursor()

    # Generate a list of all advisees for a faculty advisor
    query = """
    SELECT u.email
    FROM student s
    INNER JOIN user u ON s.user_id = u.user_id
    WHERE s.advisor_id = %s;
    """
    cursor.execute(query, (advisor_id,))
    result = cursor.fetchall()
    return result

@app.route("/generate_course_roster", methods=["GET", "POST"])
def generate_course_roster(db, course_dept, course_num):
    cursor = db.cursor()

    # Generate the course roster (list of students enrolled in a class) for a faculty instructor
    query = """
    SELECT u.email
    FROM enrollment e
    INNER JOIN user u ON e.student_uid = u.user_id
    WHERE e.crn = (
        SELECT crn
        FROM schedule
        WHERE course_dept = %s AND course_num = %s
    );
    """
    cursor.execute(query, (course_dept, course_num))
    result = cursor.fetchall()
    return result

# History of Applications that have been decided, the chair can only view this, but also able to overwrite decisions if wanted
@app.route("/history", methods=["GET", "POST"])
def history():
    """Grabs all the applications that have been decided"""

    return render_template("history.html", applications=get_history(connect_db()))

@app.route('/instructor_courses', methods=['GET'])
def instructor_courses():
    if 'user_id' not in session or session.get('role') != 'instructor':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    instructor_id = session['user_id']
    db = connect_db()
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT s.crn, c.title, s.course_dept, s.course_num, s.semester, s.year
            FROM schedule s
            JOIN course c ON s.course_dept = c.department AND s.course_num = c.course_num
            WHERE s.instructor_id = %s
        """, (instructor_id,))
        courses = cursor.fetchall()
        cursor.close()
    except Exception as e:
        db.rollback()
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('instructor_dashboard'))
    finally:
        db.close()
    
    return render_template('instructor_courses.html', courses=courses)

@app.route('/enter_grades/<int:crn>', methods=['GET', 'POST'])
def enter_grades(crn):
    db = connect_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Assume grades are submitted as part of the form data
        grades = request.form.getlist('grade')
        student_uids = request.form.getlist('student_uid')

        for student_uid, grade in zip(student_uids, grades):
            # Only update if grade is not 'IP'
            if grade != 'IP':
                cursor.execute("""
                    UPDATE enrollment
                    SET grade = %s
                    WHERE student_uid = %s AND crn = %s
                """, (grade, student_uid, crn))
        db.commit()
        flash("Grades submitted successfully", "success")
        return redirect(url_for('instructor_courses'))

    # Get students for the selected course
    cursor.execute("""
        SELECT e.student_uid, u.first_name, u.last_name, e.grade
        FROM enrollment e
        JOIN student s ON e.student_uid = s.uid
        JOIN user u ON s.user_id = u.user_id
        WHERE e.crn = %s
    """, (crn,))
    students = cursor.fetchall()
    return render_template('enter_grades.html', students=students, crn=crn)

@app.route('/view_info', methods=['GET'])
def view_info():
    if 'user_id' not in session or session.get('role') != 'instructor':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user_info = cursor.fetchone()
    return render_template('view_info.html', user_info=user_info)

app.run(debug=True, host="0.0.0.0", port=8080)
